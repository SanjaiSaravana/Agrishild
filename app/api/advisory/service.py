import os
import requests
from twilio.rest import Client
from sqlalchemy.orm import Session
from app import models
from dotenv import load_dotenv

load_dotenv()

# Twilio Configuration
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
# User specifically requested TWILIO_NUMBER
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_NUMBER") or os.getenv("TWILIO_PHONE_NUMBER")

# Weather Configuration
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city: str):
    """Fetch current weather for a city"""
    try:
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
        response = requests.get(url).json()

        if "main" not in response:
            return None, None

        temp = response["main"]["temp"]
        condition = response["weather"][0]["description"]
        return temp, condition
    except Exception as e:
        print(f"Weather lookup error: {e}")
        return None, None

def send_alert_sms(phone: str, msg: str):
    """Send a single SMS alert via Twilio"""
    if not all([TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER]):
        print("Twilio credentials not configured")
        return False
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        # We use TWILIO_PHONE_NUMBER (aliased from TWILIO_NUMBER or similar)
        message = client.messages.create(body=msg, from_=TWILIO_PHONE_NUMBER, to=phone)
        
        # Verbose success logging
        print(f"SUCCESS: Twilio accepted the request.")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        return True
    except Exception as e:
        print(f"CRITICAL ERROR: Twilio SMS failed to send to {phone}")
        print(f"Error Type: {type(e).__name__}")
        print(f"Standard Error: {str(e)}")
        
        # Specific Debugging for the user
        if "authenticate" in str(e).lower() or "permission" in str(e).lower():
            print("DEBUG: AUTHENTICATION ISSUE detected. Please verify TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN in your .env file.")
        elif "not a valid" in str(e).lower() or "is not a mobile" in str(e).lower():
            print(f"DEBUG: INVALID NUMBER detected. '{phone}' may not be in E.164 format or is not supported.")
        else:
            print("DEBUG: UNKNOWN error. Check Twilio dashboard or network connectivity.")
            
        return False

def send_bulk_alerts(db: Session):
    """Send daily alerts to all registered farmers"""
    farmers = db.query(models.AdvisoryFarmer).all()
    count = 0
    
    for farmer in farmers:
        temp, condition = get_weather(farmer.city)
        
        if temp is None:
            continue
            
        msg = f"""
🌾 Daily Agri Shield Alert

Farmer: {farmer.name}
Crop: {farmer.crop}
City: {farmer.city}

Temp: {temp}°C
Condition: {condition}

Take precautions for your {farmer.crop} today.
"""
        if send_alert_sms(farmer.phone, msg):
            count += 1
            
    return count
