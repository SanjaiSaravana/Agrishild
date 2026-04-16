from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app import database, models
from . import service

router = APIRouter()
templates = Jinja2Templates(directory="templates")

class AlertConfig(BaseModel):
    name: str
    city: str
    crop: str
    phone: str

@router.get("/", response_class=HTMLResponse)
async def alerts_page(request: Request):
    return templates.TemplateResponse("alerts.html", {"request": request})

@router.post("/configure")
async def configure_alerts(config: AlertConfig, db: Session = Depends(database.get_db)):
    # In a real app, save to DB associated with user check
    # For now, we simulate saving and trigger a welcome message
    
    # Trigger welcome message
    service.send_welcome_alert(config.name, config.city, config.crop, config.phone)
    
    # Also trigger an immediate weather daily check for gratification
    service.send_daily_alert(db, config.city, config.phone)
    
    return JSONResponse(content={"status": "success", "message": "Alerts configured successfully!"})

@router.get("/status")
async def get_alerts_status(db: Session = Depends(database.get_db)):
    # Mock status for now, since we don't have a user context yet
    # In a real app, we'd get the current user and check their sub status
    return {
        "sms_enabled": True,
        "daily_alerts": True,
        "emergency_alerts": True,
        "last_daily_alert": "2026-02-11 07:00:00"
    }

@router.post("/toggle-daily")
async def toggle_daily_alerts(db: Session = Depends(database.get_db)):
    # Mock toggle
    return {"status": "success", "message": "Daily alerts toggled"}

@router.get("/trigger-emergency-test")
async def trigger_emergency_test(db: Session = Depends(database.get_db)):
    # Test endpoint to manually trigger a weather check
    city = "Chennai"
    weather, is_dangerous, reason = service.check_rapid_weather_change(city)
    
    if is_dangerous:
        # Find all users with phone numbers and alert them
        users = db.query(models.User).filter(models.User.phone_number != None).all()
        for user in users:
            service.send_emergency_alert(db, user, reason)
        return {"status": "alert_sent", "reason": reason}
    
    return {"status": "no_danger", "weather": weather}
