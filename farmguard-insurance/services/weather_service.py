import requests
from config import Config

class WeatherService:
    @staticmethod
    def get_real_weather(lat, lon):
        api_key = Config.OPENWEATHER_API_KEY
        # 1. Real Weather Data
        weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
        
        # 2. Mock Polygon Logic (Calculates ~1 hectare square)
        offset = 0.0005 
        polygon_coords = [
            [lon - offset, lat - offset],
            [lon + offset, lat - offset],
            [lon + offset, lat + offset],
            [lon - offset, lat + offset],
            [lon - offset, lat - offset]
        ]

        try:
            # Uncomment for real API call: 
            # resp = requests.get(weather_url).json()
            
            # Simulated Response for testing
            return {
                'location_name': "Detected Farm Area",
                'temperature': {'current': 32.5},
                'rainfall': {
                    'total_30days': 45.2,
                    'threshold': 100
                },
                'ndvi': 0.78, # Real NDVI requires a Polygon ID registration
                'polygon_status': 'Registered'
            }
        except Exception as e:
            return {"error": str(e)}