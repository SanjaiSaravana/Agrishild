from fastapi import APIRouter, Request, Form, Depends, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from . import service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/personalized-alerts", response_class=HTMLResponse)
@router.get("/personalized_alerts", response_class=HTMLResponse)
async def advisory_register_page(request: Request, success: str = None):
    """Show personalized alerts registration page (handles both - and _ paths)"""
    return templates.TemplateResponse("personalized_alerts.html", {
        "request": request, 
        "success": success
    })

@router.post("/api/advisory/register")
async def advisory_register_post(
    request: Request,
    db: Session = Depends(get_db)
):
    """Register farmer and send initial weather alert using form data retrieval"""
    form_data = await request.form()
    name = form_data.get("name")
    phone = form_data.get("phone")
    city = form_data.get("city")
    crop = form_data.get("crop")

    # Save to database
    new_farmer = models.AdvisoryFarmer(name=name, phone=phone, city=city, crop=crop)
    db.add(new_farmer)
    db.commit()
    
    # Get current weather
    temp, condition = service.get_weather(city)
    
    if temp is not None:
        msg = f"""
🌾 Welcome to Agri Shield Alerts

Farmer: {name}
Crop: {crop}
City: {city}

Current Temperature: {temp}°C
Condition: {condition}

You will receive daily weather updates for your {crop}.
"""
        service.send_alert_sms(phone, msg)
        success_msg = f"Registered successfully! Initial alert sent for {city}."
    else:
        success_msg = "Registered successfully! (Weather data unavailable at the moment)"

    # Redirect back to the /personalized-alerts page (matches index.html links)
    return RedirectResponse(
        url=f"/personalized-alerts?success={success_msg}", 
        status_code=status.HTTP_303_SEE_OTHER
    )
