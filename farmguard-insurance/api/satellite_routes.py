from flask import Blueprint, jsonify
from services.satellite_service import SatelliteService

satellite_bp = Blueprint('satellite_api', __name__)

@satellite_bp.route('/ndvi')
def get_ndvi_data():
    # Mocking Sentinel-2 Satellite data
    score = 87
    status = SatelliteService.calculate_health_status(score)
    
    return jsonify({
        'health_score': score,
        'status': status,
        'water_stress': 15,
        'disease_risk': 8,
        'last_scan': '2026-02-05'
    })