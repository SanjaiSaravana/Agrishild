import httpx
import os

RESOURCE_ID = "9ef273d5-b1d0-4278-85c1-707a36330e9f"


MOCK_DATA = {
    "Tamil Nadu": [
        # Vegetables
        {"commodity": "Tomato", "market": "Chennai", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Local"},
        {"commodity": "Onion", "market": "Coimbatore", "min_price": 18, "modal_price": 22, "max_price": 26, "variety": "Red"},
        {"commodity": "Potato", "market": "Madurai", "min_price": 12, "modal_price": 15, "max_price": 18, "variety": "Desi"},
        {"commodity": "Brinjal", "market": "Chennai", "min_price": 15, "modal_price": 20, "max_price": 25, "variety": "Long"},
        {"commodity": "Cabbage", "market": "Ooty", "min_price": 10, "modal_price": 12, "max_price": 15, "variety": "Green"},
        {"commodity": "Cauliflower", "market": "Ooty", "min_price": 18, "modal_price": 22, "max_price": 28, "variety": "White"},
        {"commodity": "Carrot", "market": "Coimbatore", "min_price": 25, "modal_price": 30, "max_price": 35, "variety": "Orange"},
        {"commodity": "Beans", "market": "Madurai", "min_price": 30, "modal_price": 35, "max_price": 40, "variety": "French"},
        {"commodity": "Chilli Green", "market": "Chennai", "min_price": 40, "modal_price": 50, "max_price": 60, "variety": "Local"},
        {"commodity": "Capsicum", "market": "Coimbatore", "min_price": 35, "modal_price": 40, "max_price": 45, "variety": "Green"},
        {"commodity": "Cucumber", "market": "Chennai", "min_price": 12, "modal_price": 15, "max_price": 18, "variety": "Local"},
        {"commodity": "Radish", "market": "Madurai", "min_price": 8, "modal_price": 10, "max_price": 12, "variety": "White"},
        {"commodity": "Beetroot", "market": "Ooty", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Red"},
        {"commodity": "Drumstick", "market": "Chennai", "min_price": 30, "modal_price": 40, "max_price": 50, "variety": "Long"},
        {"commodity": "Ladies Finger", "market": "Coimbatore", "min_price": 25, "modal_price": 30, "max_price": 35, "variety": "Green"},
        {"commodity": "Bitter Gourd", "market": "Madurai", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Local"},
        {"commodity": "Bottle Gourd", "market": "Chennai", "min_price": 15, "modal_price": 18, "max_price": 22, "variety": "Green"},
        {"commodity": "Pumpkin", "market": "Coimbatore", "min_price": 12, "modal_price": 15, "max_price": 18, "variety": "Yellow"},
        {"commodity": "Ginger", "market": "Chennai", "min_price": 80, "modal_price": 100, "max_price": 120, "variety": "Fresh"},
        {"commodity": "Garlic", "market": "Madurai", "min_price": 60, "modal_price": 80, "max_price": 100, "variety": "Local"},
        {"commodity": "Coriander Leaves", "market": "Chennai", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Fresh"},
        {"commodity": "Spinach", "market": "Coimbatore", "min_price": 15, "modal_price": 20, "max_price": 25, "variety": "Green"},
        
        # Fruits
        {"commodity": "Banana", "market": "Chennai", "min_price": 30, "modal_price": 40, "max_price": 50, "variety": "Robusta"},
        {"commodity": "Mango", "market": "Salem", "min_price": 60, "modal_price": 80, "max_price": 100, "variety": "Alphonso"},
        {"commodity": "Apple", "market": "Ooty", "min_price": 120, "modal_price": 150, "max_price": 180, "variety": "Shimla"},
        {"commodity": "Orange", "market": "Coimbatore", "min_price": 50, "modal_price": 60, "max_price": 70, "variety": "Nagpur"},
        {"commodity": "Grapes", "market": "Madurai", "min_price": 80, "modal_price": 100, "max_price": 120, "variety": "Green"},
        {"commodity": "Pomegranate", "market": "Chennai", "min_price": 100, "modal_price": 120, "max_price": 150, "variety": "Bhagwa"},
        {"commodity": "Papaya", "market": "Coimbatore", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Red Lady"},
        {"commodity": "Watermelon", "market": "Madurai", "min_price": 15, "modal_price": 18, "max_price": 22, "variety": "Sugar Baby"},
        {"commodity": "Pineapple", "market": "Chennai", "min_price": 30, "modal_price": 40, "max_price": 50, "variety": "Mauritius"},
        {"commodity": "Guava", "market": "Coimbatore", "min_price": 40, "modal_price": 50, "max_price": 60, "variety": "Allahabad"},
        {"commodity": "Sapota", "market": "Madurai", "min_price": 50, "modal_price": 60, "max_price": 70, "variety": "Cricket Ball"},
        {"commodity": "Lemon", "market": "Chennai", "min_price": 40, "modal_price": 50, "max_price": 60, "variety": "Local"},
        
        # Staples
        {"commodity": "Rice", "market": "Chennai", "min_price": 40, "modal_price": 45, "max_price": 50, "variety": "Ponni"},
        {"commodity": "Coconut", "market": "Coimbatore", "min_price": 25, "modal_price": 30, "max_price": 35, "variety": "Large"},
    ],
    "Punjab": [
        {"commodity": "Wheat", "market": "Ludhiana", "min_price": 22, "modal_price": 24, "max_price": 26, "variety": "Sharbati"},
        {"commodity": "Potato", "market": "Jalandhar", "min_price": 10, "modal_price": 12, "max_price": 15, "variety": "Desi"},
        {"commodity": "Onion", "market": "Amritsar", "min_price": 15, "modal_price": 18, "max_price": 22, "variety": "Red"},
        {"commodity": "Tomato", "market": "Ludhiana", "min_price": 18, "modal_price": 22, "max_price": 26, "variety": "Hybrid"},
        {"commodity": "Cauliflower", "market": "Jalandhar", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "White"},
        {"commodity": "Cabbage", "market": "Amritsar", "min_price": 12, "modal_price": 15, "max_price": 18, "variety": "Green"},
        {"commodity": "Carrot", "market": "Ludhiana", "min_price": 22, "modal_price": 28, "max_price": 32, "variety": "Orange"},
        {"commodity": "Apple", "market": "Amritsar", "min_price": 100, "modal_price": 120, "max_price": 140, "variety": "Kashmir"},
        {"commodity": "Grapes", "market": "Jalandhar", "min_price": 70, "modal_price": 90, "max_price": 110, "variety": "Black"},
    ],
    "Maharashtra": [
        {"commodity": "Onion", "market": "Lasalgaon", "min_price": 15, "modal_price": 18, "max_price": 22, "variety": "Red"},
        {"commodity": "Tomato", "market": "Pune", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Hybrid"},
        {"commodity": "Potato", "market": "Mumbai", "min_price": 14, "modal_price": 18, "max_price": 22, "variety": "Local"},
        {"commodity": "Cabbage", "market": "Pune", "min_price": 10, "modal_price": 12, "max_price": 15, "variety": "Green"},
        {"commodity": "Cauliflower", "market": "Nashik", "min_price": 18, "modal_price": 22, "max_price": 28, "variety": "White"},
        {"commodity": "Brinjal", "market": "Mumbai", "min_price": 18, "modal_price": 22, "max_price": 26, "variety": "Long"},
        {"commodity": "Mango", "market": "Ratnagiri", "min_price": 80, "modal_price": 100, "max_price": 120, "variety": "Alphonso"},
        {"commodity": "Banana", "market": "Jalgaon", "min_price": 25, "modal_price": 35, "max_price": 45, "variety": "Grand Naine"},
        {"commodity": "Pomegranate", "market": "Solapur", "min_price": 90, "modal_price": 110, "max_price": 130, "variety": "Bhagwa"},
        {"commodity": "Cotton", "market": "Nagpur", "min_price": 5000, "modal_price": 5500, "max_price": 6000, "variety": "Long Staple"},
    ],
    # Default fallback
    "default": [
        {"commodity": "Potato", "market": "Local Mandi", "min_price": 12, "modal_price": 15, "max_price": 18, "variety": "Common"},
        {"commodity": "Onion", "market": "Local Mandi", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Red"},
        {"commodity": "Tomato", "market": "Local Mandi", "min_price": 25, "modal_price": 30, "max_price": 35, "variety": "Hybrid"},
        {"commodity": "Cabbage", "market": "Local Mandi", "min_price": 10, "modal_price": 12, "max_price": 15, "variety": "Green"},
        {"commodity": "Cauliflower", "market": "Local Mandi", "min_price": 18, "modal_price": 22, "max_price": 28, "variety": "White"},
        {"commodity": "Carrot", "market": "Local Mandi", "min_price": 20, "modal_price": 25, "max_price": 30, "variety": "Orange"},
        {"commodity": "Brinjal", "market": "Local Mandi", "min_price": 15, "modal_price": 20, "max_price": 25, "variety": "Local"},
        {"commodity": "Beans", "market": "Local Mandi", "min_price": 28, "modal_price": 32, "max_price": 38, "variety": "French"},
        {"commodity": "Banana", "market": "Local Mandi", "min_price": 30, "modal_price": 40, "max_price": 50, "variety": "Local"},
        {"commodity": "Apple", "market": "Local Mandi", "min_price": 100, "modal_price": 120, "max_price": 140, "variety": "Shimla"},
        {"commodity": "Orange", "market": "Local Mandi", "min_price": 50, "modal_price": 60, "max_price": 70, "variety": "Nagpur"},
        {"commodity": "Grapes", "market": "Local Mandi", "min_price": 70, "modal_price": 90, "max_price": 110, "variety": "Green"},
    ]
}

async def fetch_mandi_data(state: str, district: str):
    api_key = os.getenv('AGMARKNET_API_KEY')
    
    # Return mock data if key is missing or for testing reliability
    if not api_key:
        print(f"Using Mock Data for {state}")
        return MOCK_DATA.get(state, MOCK_DATA["default"])

    url = (f"https://api.data.gov.in/resource/{RESOURCE_ID}?"
           f"api-key={api_key}&format=json"
           f"&filters[state]={state}&filters[district]={district}")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, timeout=10.0)
            data = response.json()
            records = data.get('records', [])
            if not records:
                return MOCK_DATA.get(state, MOCK_DATA["default"])
            return records
        except Exception as e:
            print(f"API Error: {e}")
            return MOCK_DATA.get(state, MOCK_DATA["default"])