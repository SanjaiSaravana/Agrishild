import requests
import json
from config import Config

class SatelliteService:
    @staticmethod
    def create_farm_polygon(lat, lon):
        """Creates a 1-hectare square polygon around the GPS point."""
        # Offset for ~100m (roughly 0.0009 degrees)
        offset = 0.0009
        
        # Define 4 points of the square (Polygon must close at the start point)
        coords = [
            [lon - offset, lat - offset],
            [lon + offset, lat - offset],
            [lon + offset, lat + offset],
            [lon - offset, lat + offset],
            [lon - offset, lat - offset]
        ]
        
        url = f"http://api.agromonitoring.com/agro/1.0/polygons?appid={Config.AGRO_API_KEY}"
        payload = {
            "name": f"Farm_{lat}_{lon}",
            "geo_json": {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coords]
                }
            }
        }
        
        response = requests.post(url, json=payload)
        return response.json() # Returns 'id' of the polygon for future NDVI checks

    @staticmethod
    def get_ndvi_score(polygon_id):
        """Fetches the latest NDVI score for a registered polygon."""
        url = f"http://api.agromonitoring.com/agro/1.0/ndvi/history?polyid={polygon_id}&appid={Config.AGRO_API_KEY}"
        # Simplified: In a real app, you'd fetch the latest timestamped score
        return 87 # Mocked until real polygon has data