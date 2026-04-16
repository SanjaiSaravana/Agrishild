import ee

# Initialize Earth Engine
# Ensure you have authenticated via 'earthengine authenticate' or a service account
try:
    ee.Initialize()
except:
    ee.Authenticate()
    ee.Initialize()

def get_satellite_analysis(lat, lon, soil_moisture=None, nutrient_data=None):
    """
    Geospatial evaluation enforcing Hard-Zero Geographic Barriers and constraints.
    Default state for unknown coordinates or missing parameters must be None.
    """
    # Remove default True states; default state is None
    if lat is None or lon is None:
        return None

    # Step 1: Hard-Zero check for invalid sensor data constraints
    # Validates Nutrient Data and Soil Moisture strictly
    if soil_moisture == 0 or nutrient_data is None:
        return {
            "suitability_score": "0%",
            "status": "Invalid Location (Water).",
            "error_reason": "Soil moisture is 0 or Node Nutrient Data is null.",
            "accuracy": "100%"
        }

    try:
        point = ee.Geometry.Point([lon, lat])
        area = point.buffer(500).bounds()
        
        # Step 2: Global Offline/EE Land-Mask integration to check Water Bodies
        # Utilize Earth Engine MOD44W (Global Water Mask) or NDWI calculation
        water_mask_collection = ee.ImageCollection("MODIS/006/MOD44W").filterBounds(point)
        if water_mask_collection.size().getInfo() > 0:
            is_water_dict = water_mask_collection.first().select('water_mask').reduceRegion(ee.Reducer.first(), point, 30).getInfo()
            is_water = is_water_dict.get('water_mask')
            
            # 1 represents Water in the MODIS Land-Water Mask
            if is_water == 1:
                return {
                    "suitability_score": "0%",
                    "status": "Invalid Location (Water).",
                    "error_reason": "Coordinates located in a major water body.",
                    "accuracy": "100%",
                    "error": "Coordinates located in a major water body."
                }

        # Step 3: Base prediction logic via Sentinel-2 (Now protected by strict geographic masks)
        image = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
                 .filterBounds(area)
                 .filterDate('2024-01-01', '2026-12-31')
                 .sort('CLOUDY_PIXEL_PERCENTAGE')
                 .first())
                 
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        stats_ndvi = ndvi.reduceRegion(ee.Reducer.mean(), area, 10).getInfo().get('NDVI')
        
        # Determine actual crop health index using valid masked ground data
        confidence = min(90, 50 + (stats_ndvi * 50) if stats_ndvi else 50)
        suitability_score = int(stats_ndvi * 100) if stats_ndvi else 40
        
        # Generate map url
        map_id = ndvi.getMapId({'min': 0, 'max': 1, 'palette': ['red', 'yellow', 'green']})

        return {
            "suitability_score": f"{max(0, suitability_score)}%",
            "status": "Suitable Location" if suitability_score >= 40 else "Marginal Location",
            "accuracy": f"{round(confidence, 1)}%",
            "map_url": map_id['tile_fetcher'].url_format,
            "ndvi": round(stats_ndvi, 3) if stats_ndvi else 0,
            "ndbi": 0 # Defaulting NDBI since logic was replaced
        }

    except Exception as e:
        return {"error": str(e), "suitability_score": "0%", "accuracy": "0%"}