import datetime
from datetime import timedelta
from typing import Optional

from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash

from app.database import get_db
from app.models import BiddingUser, Crop, Bid

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# --- Helper Functions ---
def get_current_bidding_user(request: Request, db: Session = Depends(get_db)) -> Optional[BiddingUser]:
    """Get the currently logged in bidding user from session"""
    user_id = request.session.get("bidding_user_id")
    if user_id:
        return db.query(BiddingUser).filter(BiddingUser.id == user_id).first()
    return None

def flash(request: Request, message: str, category: str = "info"):
    """Add a flash message to the session"""
    if "_bidding_messages" not in request.session:
        request.session["_bidding_messages"] = []
    request.session["_bidding_messages"].append({"message": message, "category": category})

from jinja2 import pass_context

@pass_context
def get_flashed_messages(context: dict, with_categories: bool = False):
    """Get and clear flash messages from session"""
    request = context.get("request")
    if not request:
        return []
    messages = request.session.pop("_bidding_messages", [])
    if with_categories:
        return [(m["category"], m["message"]) for m in messages]
    return [m["message"] for m in messages]

templates.env.globals['get_flashed_messages'] = get_flashed_messages

def mock_ai_grading(name, description):
    """Mock AI grading function"""
    score = (len(name) + len(description or '')) % 10
    if score > 7: return 'A'
    elif score > 3: return 'B'
    else: return 'C'

# --- Routes ---

@router.get("/auth", response_class=HTMLResponse)
async def bidding_auth(request: Request, db: Session = Depends(get_db)):
    """Show bidding authentication page"""
    current_user = get_current_bidding_user(request, db)
    if current_user:
        return RedirectResponse(url="/bidding/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("bidding_auth.html", {"request": request, "current_user": current_user})

@router.post("/auth")
async def bidding_auth_post(
    request: Request,
    action: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("bidder"),
    db: Session = Depends(get_db)
):
    """Handle bidding login and registration"""
    if action == "register":
        if db.query(BiddingUser).filter(BiddingUser.username == username).first():
            flash(request, "Username already exists.", "error")
            return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
        
        hashed_pw = generate_password_hash(password)
        new_user = BiddingUser(username=username, password=hashed_pw, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        request.session["bidding_user_id"] = new_user.id
        return RedirectResponse(url="/bidding/dashboard", status_code=status.HTTP_302_FOUND)

    elif action == "login":
        user = db.query(BiddingUser).filter(BiddingUser.username == username).first()
        if user and check_password_hash(user.password, password):
            request.session["bidding_user_id"] = user.id
            return RedirectResponse(url="/bidding/dashboard", status_code=status.HTTP_302_FOUND)
        else:
            flash(request, "Invalid credentials.", "error")
            return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)

@router.get("/logout")
async def bidding_logout(request: Request):
    """Logout from bidding system"""
    request.session.pop("bidding_user_id", None)
    return RedirectResponse(url="/smart-bidding", status_code=status.HTTP_302_FOUND)

@router.get("/dashboard")
async def bidding_dashboard(request: Request, db: Session = Depends(get_db)):
    """Redirect to appropriate dashboard based on user role"""
    current_user = get_current_bidding_user(request, db)
    if not current_user:
        return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
    if current_user.role == 'farmer':
        return RedirectResponse(url="/bidding/farmer/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/bidding/bidder/dashboard", status_code=status.HTTP_302_FOUND)

@router.get("/farmer/dashboard", response_class=HTMLResponse)
async def farmer_dashboard(request: Request, db: Session = Depends(get_db)):
    """Show farmer dashboard"""
    current_user = get_current_bidding_user(request, db)
    if not current_user or current_user.role != 'farmer':
        return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
    crops = db.query(Crop).filter(Crop.farmer_id == current_user.id).all()
    revenue = sum([c.highest_bid() for c in crops])
    return templates.TemplateResponse("bidding_farmer_dashboard.html", {
        "request": request, 
        "current_user": current_user, 
        "crops": crops, 
        "revenue": revenue
    })

@router.get("/bidder/dashboard", response_class=HTMLResponse)
async def bidder_dashboard(request: Request, db: Session = Depends(get_db)):
    """Show bidder dashboard"""
    current_user = get_current_bidding_user(request, db)
    if not current_user or current_user.role != 'bidder':
        return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
    all_crops = db.query(Crop).all()
    active_crops = [crop for crop in all_crops if crop.is_active()]
    expired_crops = [crop for crop in all_crops if not crop.is_active()]
    expired_crops.sort(key=lambda x: x.end_time, reverse=True)
    
    return templates.TemplateResponse("bidding_bidder_dashboard.html", {
        "request": request, 
        "current_user": current_user, 
        "active_crops": active_crops, 
        "expired_crops": expired_crops
    })

@router.post("/crop/add")
async def add_crop(
    request: Request,
    name: str = Form(...),
    quantity: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    duration: int = Form(5),
    db: Session = Depends(get_db)
):
    """Add a new crop listing"""
    current_user = get_current_bidding_user(request, db)
    if not current_user or current_user.role != 'farmer':
        return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
    
    grade = mock_ai_grading(name, description)
    end_time = datetime.datetime.now() + timedelta(minutes=duration)

    new_crop = Crop(
        farmer_id=current_user.id,
        name=name,
        quantity=quantity,
        base_price=price,
        description=description,
        ai_grade=grade,
        end_time=end_time
    )
    db.add(new_crop)
    db.commit()
    flash(request, f'Crop listed! AI Grade: {grade}. Auction ends at {end_time.strftime("%H:%M")}', 'success')
    return RedirectResponse(url="/bidding/farmer/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/crop/delete/{id}")
async def delete_crop(id: int, request: Request, db: Session = Depends(get_db)):
    """Delete a crop listing"""
    current_user = get_current_bidding_user(request, db)
    crop = db.query(Crop).filter(Crop.id == id).first()
    if crop and current_user and crop.farmer_id == current_user.id:
        db.delete(crop)
        db.commit()
        flash(request, 'Crop deleted.', 'success')
    return RedirectResponse(url="/bidding/farmer/dashboard", status_code=status.HTTP_302_FOUND)

@router.post("/bid/{crop_id}")
async def place_bid(
    crop_id: int,
    request: Request,
    amount_str: str = Form(..., alias="amount"),
    db: Session = Depends(get_db)
):
    """Place a bid on a crop"""
    current_user = get_current_bidding_user(request, db)
    if not current_user or current_user.role != 'bidder':
        return RedirectResponse(url="/bidding/auth", status_code=status.HTTP_302_FOUND)
    
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404)
    
    if not crop.is_active():
        flash(request, 'Auction has ended.', 'error')
        return RedirectResponse(url="/bidding/bidder/dashboard", status_code=status.HTTP_302_FOUND)

    current_highest = crop.highest_bid()
    threshold = max(crop.base_price, current_highest)

    if amount_str == 'auto_5':
        amount = threshold + 5
    else:
        try:
            amount = float(amount_str)
        except ValueError:
            flash(request, 'Invalid bid amount.', 'error')
            return RedirectResponse(url="/bidding/bidder/dashboard", status_code=status.HTTP_302_FOUND)

    if amount <= threshold:
         flash(request, f'Bid must be higher than ${threshold}.', 'error')
    else:
        new_bid = Bid(crop_id=crop.id, bidder_id=current_user.id, amount=amount)
        db.add(new_bid)
        db.commit()
        flash(request, 'Bid placed successfully!', 'success')
        
    return RedirectResponse(url="/bidding/bidder/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@router.post("/meet/update/{crop_id}")
async def update_meet(
    crop_id: int,
    request: Request,
    meet_link: str = Form(...),
    db: Session = Depends(get_db)
):
    """Update meeting link for a crop"""
    current_user = get_current_bidding_user(request, db)
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if crop and current_user and crop.farmer_id == current_user.id:
        crop.meet_link = meet_link
        db.commit()
        flash(request, 'Meeting link updated.', 'success')
    return RedirectResponse(url="/bidding/farmer/dashboard", status_code=status.HTTP_303_SEE_OTHER)
