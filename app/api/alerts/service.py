import os
import requests
from twilio.rest import Client
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from app import models

load_dotenv()

# Twilio config
ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

client = Client(ACCOUNT_SID, AUTH_TOKEN) if ACCOUNT_SID and AUTH_TOKEN else None

def get_weather(city: str):
    if not WEATHER_API_KEY:
        return None
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    try:
        response = requests.get(url).json()
        if "main" not in response:
            return None
        return response
    except Exception:
        return None

def send_sms(to_phone: str, message: str):
    """
    Sends an SMS using Twilio if credentials are availble, otherwise logs to console.
    """
    if not to_phone:
        print("Skipping SMS: No phone number provided.")
        return

    if not client or not TWILIO_NUMBER:
        print(f"------------ SMS SIMULATION ------------")
        print(f"TO: {to_phone}")
        print(f"MSG: {message}")
        print(f"----------------------------------------")
        return
    
    try:
        client.messages.create(body=message, from_=TWILIO_NUMBER, to=to_phone)
        print(f"SMS sent successfully to {to_phone}")
    except Exception as e:
        print(f"Failed to send SMS to {to_phone}: {e}")

def check_rapid_weather_change(city: str):
    weather = get_weather(city)
    if not weather:
        return None, False, ""
    
    main = weather.get("main", {})
    wind = weather.get("wind", {})
    weather_desc = weather.get("weather", [{}])[0].get("main", "").lower()
    
    temp = main.get("temp")
    wind_speed = wind.get("speed", 0)
    
    is_dangerous = False
    reason = ""
    
    if wind_speed > 15: # High wind
        is_dangerous = True
        reason = "high wind flow"
    elif "rain" in weather_desc or "drizzle" in weather_desc:
        is_dangerous = True
        reason = "heavy rain"
    elif "storm" in weather_desc or "thunderstorm" in weather_desc:
        is_dangerous = True
        reason = "storm alert"
        
    return weather, is_dangerous, reason

def send_daily_alert(db: Session = None, city: str = "Chennai", phone: str = None):
    """
    Sends a daily weather snapshot.
    """
    weather = get_weather(city)
    if weather:
        temp = weather["main"]["temp"]
        desc = weather["weather"][0]["description"]
        msg = f"🌾 AgriShield Daily: Morning! In {city}, it's {temp}°C with {desc}. Good day for farming!"
        send_sms(phone, msg)

def send_welcome_alert(name: str, city: str, crop: str, phone: str):
    """
    Sends an immediate confirmation message upon configuration.
    """
    msg = f"✅ AgriShield Alerts Active! Hi {name}, we are now monitoring {crop} in {city} for you. We will notify you of any risks."
    send_sms(phone, msg)

def send_emergency_alert(db: Session, user: models.User, reason: str):
    if user.phone_number:
        msg = f"🚨 AgriShield ALERT: Rapid weather change detected ({reason})! Please take precautions for your crops."
        send_sms(user.phone_number, msg)
