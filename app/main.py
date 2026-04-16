from fastapi import FastAPI, Request, Depends
from sqlalchemy.orm import Session
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import os
from dotenv import load_dotenv

# Import the routers from your modular folders
# These will be created in your app/api/ folders
from app.api.chatbot import router as chat_router
from app.api.market import router as market_router
from app.api import auth
from app import models, database

# Create Database Tables
models.Base.metadata.create_all(bind=database.engine)

import os
import asyncio
from datetime import datetime, time as dtime
from dotenv import load_dotenv
from app.api.alerts import service
from app.api.advisory import router as advisory_router, service as advisory_service


# ... (models/database setup)

load_dotenv()

app = FastAPI(title="AgriShield Pro")

# Add Session Middleware for bidding system
app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))

async def weather_monitoring_task():
    while True:
        # Emergency check every 30 minutes
        # In a real app, you'd iterate over users and their specific cities
        db = database.SessionLocal()
        try:
            city = "Chennai" # Default test city
            weather, is_dangerous, reason = service.check_rapid_weather_change(city)
            if is_dangerous:
                users = db.query(models.User).filter(models.User.phone_number != None).all()
                for user in users:
                    service.send_emergency_alert(db, user, reason)
            
            # Daily alert check at 07:00 AM
            now = datetime.now()
            if now.hour == 7 and now.minute < 30:
                service.send_daily_alert(db)
                # New Personalized SMS alerts (Agri Advisory System)
                advisory_service.send_bulk_alerts(db)
                # Sleep longer to avoid sending multiple times in the same window
                await asyncio.sleep(1800) 
                
        except Exception as e:
            print(f"Background monitoring error: {e}")
        finally:
            db.close()
            
        await asyncio.sleep(1800) # Check every 30 mins

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(weather_monitoring_task())

# Add CORS middleware to allow frontend to communicate with backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 1. Static Files (CSS, JS, Images)
# The 'name="static"' is the key used in url_for('static', ...)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 2. Templates (HTML)
templates = Jinja2Templates(directory="templates")

# 3. Include Microservice Routers
# This keeps your code clean as you add Weather, Soil, etc.
app.include_router(chat_router.router, prefix="/api/chat", tags=["AI"])
app.include_router(market_router.router, prefix="/api/market", tags=["Market"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])

from app.api.crop_monitor import router as crop_router
app.include_router(crop_router.router, prefix="/api/crop-monitor", tags=["CropMonitor"])

from app.api.flora_scan import router as flora_router
app.include_router(flora_router.router, prefix="/api/flora-scan", tags=["FloraScan"])

from app.api.alerts import router as alerts_router
app.include_router(alerts_router.router, prefix="/api/alerts", tags=["Alerts"])
app.include_router(advisory_router.router, prefix="", tags=["Advisory"])


# --- PAGE ROUTES ---

@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/alerts", response_class=HTMLResponse)
async def alerts_page_ui(request: Request):
    return templates.TemplateResponse("alerts.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page_ui(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/market", response_class=HTMLResponse)
async def market_page_ui(request: Request):
    return templates.TemplateResponse("market.html", {"request": request})

@app.get("/crop-monitor", response_class=HTMLResponse)
async def crop_monitor_page_ui(request: Request):
    return templates.TemplateResponse("crop_monitor.html", {"request": request})

@app.get("/flora-scan", response_class=HTMLResponse)
async def flora_scan_page_ui(request: Request):
    return templates.TemplateResponse("flora_scan.html", {"request": request})

from app.api.insurance import router as insurance_router
app.include_router(insurance_router.router, prefix="/api/insurance", tags=["Insurance"])

@app.get("/insurance", response_class=HTMLResponse)
async def insurance_page_ui(request: Request):
    return templates.TemplateResponse("insurance.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page_ui(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/signup", response_class=HTMLResponse)
async def signup_page_ui(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

from app.api.optimal_selling import AgriLogic

@app.get("/optimal-selling", response_class=HTMLResponse)
async def optimal_selling_page(request: Request):
    days_lookup = AgriLogic.get_calendar_data_dict()
    # February 2026 starts on Sunday. Offset = 0 empty slots.
    return templates.TemplateResponse("optimal_selling.html", {
        "request": request,
        "days_dict": days_lookup,
        "offset": range(0) 
    })

# --- Bidding System Integration ---
from app.api.bidding import router as bidding_router
app.include_router(bidding_router.router, prefix="/bidding", tags=["Bidding"])

@app.get("/smart-bidding", response_class=HTMLResponse)
async def smart_bidding_page(request: Request):
    return templates.TemplateResponse("smart_bidding.html", {"request": request})

@app.get("/personalized-alerts")
async def personalized_alerts_redirect():
    return RedirectResponse(url="http://127.0.0.1:5001/personalized_alerts")


