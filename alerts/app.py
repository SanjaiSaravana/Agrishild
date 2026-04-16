from flask import Flask, render_template, request
from twilio.rest import Client
from dotenv import load_dotenv
import os
import requests
from database import init_db, add_farmer, get_farmers

load_dotenv()

app = Flask(__name__)

# Initialize DB
init_db()

# Twilio config
account_sid = os.getenv("TWILIO_ACCOUNT_SID")
auth_token = os.getenv("TWILIO_AUTH_TOKEN")
twilio_number = os.getenv("TWILIO_PHONE_NUMBER")
client = Client(account_sid, auth_token)

# Weather API
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")


def get_weather(city):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
    response = requests.get(url).json()

    if "main" not in response:
        return None, None

    temp = response["main"]["temp"]
    condition = response["weather"][0]["description"]

    return temp, condition


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

        client.messages.create(body=msg, from_=twilio_number, to=phone)


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        city = request.form["city"]
        crop = request.form["crop"]

        # Save farmer
        add_farmer(name, phone, city, crop)

        temp, condition = get_weather(city)

        if temp is None:
            return render_template("index.html", success="Invalid city name")

        message_text = f"""
🌾 Smart Agri Advisory

Farmer: {name}
Crop: {crop}
City: {city}

Temperature: {temp}°C
Condition: {condition}

Take precautions for {crop}.
"""

        client.messages.create(
            body=message_text,
            from_=twilio_number,
            to=phone
        )

        return render_template("index.html", success="Farmer registered & SMS sent!")

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
