import datetime
from datetime import timedelta
from typing import Optional

from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, ForeignKey, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from werkzeug.security import generate_password_hash, check_password_hash

# --- Database Setup ---
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Models ---
class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)  # 'farmer' or 'bidder'

    @property
    def is_authenticated(self):
        return True

class Crop(Base):
    __tablename__ = "crop"
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    ai_grade = Column(String(10), nullable=False)
    meet_link = Column(String(200), nullable=True)
    end_time = Column(DateTime, nullable=False)

    farmer = relationship("User", backref="crops")
    bids = relationship("Bid", back_populates="crop", cascade="all, delete-orphan")

    def highest_bid(self):
        if self.bids:
            return max([bid.amount for bid in self.bids])
        return 0

    def is_active(self):
        return datetime.datetime.now() < self.end_time

    def get_winner(self):
        if self.bids and not self.is_active():
            highest = max(self.bids, key=lambda b: b.amount)
            return highest.bidder.username
        return None

class Bid(Base):
    __tablename__ = "bid"
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crop.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

    crop = relationship("Crop", back_populates="bids")
    bidder = relationship("User", backref="bids")

# Create tables
Base.metadata.create_all(bind=engine)

# --- FastAPI Setup ---
app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key="your-secret-key-123")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# --- Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(request: Request, db: Session = Depends(get_db)) -> Optional[User]:
    user_id = request.session.get("user_id")
    if user_id:
        return db.query(User).filter(User.id == user_id).first()
    return None

# Template Helper for flashing messages (Flask-like)
def flash(request: Request, message: str, category: str = "info"):
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append({"message": message, "category": category})

from jinja2 import pass_context

@pass_context
def get_flashed_messages(context: dict, with_categories: bool = False):
    request = context.get("request")
    if not request:
        return []
    messages = request.session.pop("_messages", [])
    if with_categories:
        return [(m["category"], m["message"]) for m in messages]
    return [m["message"] for m in messages]

templates.env.globals['get_flashed_messages'] = get_flashed_messages

# --- Helper Functions ---
def mock_ai_grading(name, description):
    score = (len(name) + len(description or '')) % 10
    if score > 7: return 'A'
    elif score > 3: return 'B'
    else: return 'C'

# --- Routes ---
@app.get("/", response_class=HTMLResponse)
async def index(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("index.html", {"request": request, "current_user": current_user})

@app.get("/auth", response_class=HTMLResponse)
async def auth(request: Request, current_user: User = Depends(get_current_user)):
    if current_user:
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("auth.html", {"request": request, "current_user": current_user})

@app.post("/auth")
async def auth_post(
    request: Request,
    action: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    role: str = Form("bidder"),
    db: Session = Depends(get_db)
):
    if action == "register":
        if db.query(User).filter(User.username == username).first():
            flash(request, "Username already exists.", "error")
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
        
        hashed_pw = generate_password_hash(password)
        new_user = User(username=username, password=hashed_pw, role=role)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        request.session["user_id"] = new_user.id
        return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)

    elif action == "login":
        user = db.query(User).filter(User.username == username).first()
        if user and check_password_hash(user.password, password):
            request.session["user_id"] = user.id
            return RedirectResponse(url="/dashboard", status_code=status.HTTP_302_FOUND)
        else:
            flash(request, "Invalid credentials.", "error")
            return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

@app.get("/logout")
async def logout(request: Request):
    request.session.clear()
    return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)

@app.get("/dashboard")
async def dashboard(request: Request, current_user: User = Depends(get_current_user)):
    if not current_user:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    if current_user.role == 'farmer':
        return RedirectResponse(url="/farmer/dashboard", status_code=status.HTTP_302_FOUND)
    return RedirectResponse(url="/bidder/dashboard", status_code=status.HTTP_302_FOUND)

@app.get("/farmer/dashboard", response_class=HTMLResponse)
async def farmer_dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user or current_user.role != 'farmer':
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    crops = db.query(Crop).filter(Crop.farmer_id == current_user.id).all()
    revenue = sum([c.highest_bid() for c in crops])
    return templates.TemplateResponse("farmer_dashboard.html", {
        "request": request, 
        "current_user": current_user, 
        "crops": crops, 
        "revenue": revenue
    })

@app.get("/bidder/dashboard", response_class=HTMLResponse)
async def bidder_dashboard(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not current_user or current_user.role != 'bidder':
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    all_crops = db.query(Crop).all()
    active_crops = [crop for crop in all_crops if crop.is_active()]
    expired_crops = [crop for crop in all_crops if not crop.is_active()]
    expired_crops.sort(key=lambda x: x.end_time, reverse=True)
    
    return templates.TemplateResponse("bidder_dashboard.html", {
        "request": request, 
        "current_user": current_user, 
        "active_crops": active_crops, 
        "expired_crops": expired_crops
    })

@app.post("/crop/add")
async def add_crop(
    request: Request,
    name: str = Form(...),
    quantity: str = Form(...),
    price: float = Form(...),
    description: str = Form(None),
    duration: int = Form(5),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user.role != 'farmer':
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
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
    return RedirectResponse(url="/farmer/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.get("/crop/delete/{id}")
async def delete_crop(id: int, request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    crop = db.query(Crop).filter(Crop.id == id).first()
    if crop and current_user and crop.farmer_id == current_user.id:
        db.delete(crop)
        db.commit()
        flash(request, 'Crop deleted.', 'success')
    return RedirectResponse(url="/farmer/dashboard", status_code=status.HTTP_302_FOUND)

@app.post("/bid/{crop_id}")
async def place_bid(
    crop_id: int,
    request: Request,
    amount_str: str = Form(..., alias="amount"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not current_user or current_user.role != 'bidder':
        return RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if not crop:
        raise HTTPException(status_code=404)
    
    if not crop.is_active():
        flash(request, 'Auction has ended.', 'error')
        return RedirectResponse(url="/bidder/dashboard", status_code=status.HTTP_302_FOUND)

    current_highest = crop.highest_bid()
    threshold = max(crop.base_price, current_highest)

    if amount_str == 'auto_5':
        amount = threshold + 5
    else:
        try:
            amount = float(amount_str)
        except ValueError:
            flash(request, 'Invalid bid amount.', 'error')
            return RedirectResponse(url="/bidder/dashboard", status_code=status.HTTP_302_FOUND)

    if amount <= threshold:
         flash(request, f'Bid must be higher than ${threshold}.', 'error')
    else:
        new_bid = Bid(crop_id=crop.id, bidder_id=current_user.id, amount=amount)
        db.add(new_bid)
        db.commit()
        flash(request, 'Bid placed successfully!', 'success')
        
    return RedirectResponse(url="/bidder/dashboard", status_code=status.HTTP_303_SEE_OTHER)

@app.post("/meet/update/{crop_id}")
async def update_meet(
    crop_id: int,
    request: Request,
    meet_link: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    crop = db.query(Crop).filter(Crop.id == crop_id).first()
    if crop and current_user and crop.farmer_id == current_user.id:
        crop.meet_link = meet_link
        db.commit()
        flash(request, 'Meeting link updated.', 'success')
    return RedirectResponse(url="/farmer/dashboard", status_code=status.HTTP_303_SEE_OTHER)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
