from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client
from dotenv import load_dotenv
import os
import requests
import asyncio
from datetime import datetime
from database import init_db, add_farmer, get_farmers
from contextlib import asynccontextmanager
import uvicorn

load_dotenv()

# Twilio config
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(account_sid, auth_token)

# Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if "main" not in response:
            return None, None
        temp = response["main"]["temp"]
        condition = response["weather"][0]["description"]
        return temp, condition
    except Exception as e:
        print(f"Error fetching weather: {e}")
        return None, None

def send_bulk_sms():
    farmers = get_farmers()
    for name, phone, city, crop in farmers:
        temp, condition = get_weather(city)
        if temp is None:
            continue
        msg = f"""
🌾 Daily Agri Alert

Farmer: {name}
Crop: {crop}
City: {city}

Temp: {temp}°C
Condition: {condition}

Take precautions today.
"""
        try:
            client.messages.create(body=msg, from_=twilio_number, to=phone)
            print(f"Sent SMS to {name} ({phone})")
        except Exception as e:
            print(f"Failed to send SMS to {name}: {e}")

async def run_scheduler():
    last_sent_date = None
    while True:
        now = datetime.now()
        # Run every day at 07:00 AM
        if now.hour == 7 and now.minute == 0 and last_sent_date != now.date():
            print("Running scheduled bulk SMS task...")
            send_bulk_sms()
            last_sent_date = now.date()
        
        # Check every 60 seconds
        await asyncio.sleep(60)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    init_db()
    print("Database initialized.")
    # Start scheduler task
    scheduler_task = asyncio.create_task(run_scheduler())
    yield
    # Shutdown logic
    scheduler_task.cancel()
    try:
        await scheduler_task
    except asyncio.CancelledError:
        print("Scheduler task cancelled.")

# Get absolute paths to avoid routing issues
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")
# Point to the main templates folder one level up
TEMPLATES_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")

app = FastAPI(lifespan=lifespan)

# Mount static files correctly
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Initialize templates with absolute path
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.get("/personalized_alerts", response_class=HTMLResponse)
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("personalized_alerts.html", {"request": request})

@app.post("/api/advisory/register", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def register(
    request: Request,
    name: str = Form(...),
    phone: str = Form(...),
    city: str = Form(...),
    crop: str = Form(...)
):
    # Save farmer
    add_farmer(name, phone, city, crop)
    temp, condition = get_weather(city)

    if temp is None:
        return templates.TemplateResponse(
            "personalized_alerts.html", 
            {"request": request, "success": "Invalid city name or weather service unavailable."}
        )

    # --- Real-Time Number Cleanup ---
    # Strip spaces and dashes
    clean_phone = phone.strip().replace(" ", "").replace("-", "")
    # Ensure it starts with +91
    if not clean_phone.startswith("+"):
        if clean_phone.startswith("91") and len(clean_phone) > 10:
            clean_phone = "+" + clean_phone
        else:
            clean_phone = "+91" + clean_phone.lstrip("0")
    
    print(f"DEBUG: Input Number: {phone} | Cleaned Number: {clean_phone}")

    message_text = f"""
🌾 Smart Agri Advisory

Farmer: {name}
Crop: {crop}
City: {city}

Temperature: {temp}°C
Condition: {condition}

Take precautions for {crop}.
"""
    try:
        # 1. Create message (Initial trigger)
        message = client.messages.create(
            body=message_text,
            from_=twilio_number,
            to=clean_phone
        )
        print(f"DEBUG: Message Triggered -> SID: {message.sid} | Status: {message.status}")
        
        # 2. Real-Time Delay (8 seconds for carrier processing)
        print("DEBUG: Waiting 8 seconds for carrier response...")
        await asyncio.sleep(8)
        
        # 3. Fetch Real-Time Status
        check_msg = client.messages(message.sid).fetch()
        
        # 4. Print Debug Details
        print("\n" + "#"*20 + " REAL-TIME DIAGNOSTICS " + "#"*20)
        print(f"FINAL STATUS  : {check_msg.status}")
        print(f"ERROR CODE    : {check_msg.error_code}")
        print(f"ERROR MESSAGE : {check_msg.error_message}")
        print("#"*63 + "\n")
        
        if check_msg.status in ['undelivered', 'failed']:
            print(f"Carrier Block Detected! Cross-reference Code {check_msg.error_code}")
        else:
            print(f"Message passed to carrier: {check_msg.status}")

    except Exception as e:
        print(f"CRITICAL ERROR: Twilio API call failed: {e}")

    return templates.TemplateResponse(
        "personalized_alerts.html", 
        {"request": request, "success": "Farmer registered & SMS sent!"}
    )

if __name__ == "__main__":
    uvicorn.run("app:app", host="127.0.0.1", port=5001, reload=True)
