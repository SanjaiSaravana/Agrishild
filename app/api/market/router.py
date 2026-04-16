from fastapi import APIRouter, Request
from .service import fetch_mandi_data

router = APIRouter()

@router.post("/tracker")
async def market_tracker(request: Request):
    data = await request.json()
    state = data.get("state")
    district = data.get("district")
    
    # Simple Reverse Geocoding Logic (Mock/Static for stability)
    # in a real app, you'd use a geocoding library here if lat/lon provided
    if not state and data.get("lat"):
       # Mocking reverse geo for demo stability
       state = "Tamil Nadu" 
       district = "Chennai"

    # Default if everything fails
    if not state:
        state = "Tamil Nadu"
        district = "Chennai"

    print(f"Fetching data for State: {state}, District: {district}")
    records = await fetch_mandi_data(state, district)
    
    return {
        "status": "success", 
        "data": records,
        "location": {"state": state, "district": district}
    }