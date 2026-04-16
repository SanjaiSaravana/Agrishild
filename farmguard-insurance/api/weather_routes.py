from flask import Blueprint, request, jsonify
from services.weather_service import WeatherService

weather_bp = Blueprint('weather_api', __name__)

@weather_bp.route('/current')
def get_current_weather():
    # Capture lat/lon from the browser's request
    lat = request.args.get('lat', default=19.0760, type=float)
    lon = request.args.get('lon', default=72.8777, type=float)
    
    data = WeatherService.get_real_weather(lat, lon)
    return jsonify(data)