import json
import os
from datetime import datetime, timedelta

# Path to the data file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "data", "calendar_2026.json")

class AgriLogic:
    @staticmethod
    def load_data():
        """Loads the raw festival and muhurtham data from JSON."""
        if not os.path.exists(DATA_FILE):
            return []
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)

    @staticmethod
    def get_enriched_calendar():
        """
        Processes raw dates to add 'Action Dates'.
        Example: If Pongal is Jan 14, it flags Jan 12 as 'Harvest Day'.
        """
        raw_data = AgriLogic.load_data()
        enriched_data = []

        for item in raw_data:
            event_date = datetime.strptime(item["date"], "%Y-%m-%d")
            
            # 1. Peak Sale Window (The Day of and Day Before)
            item["peak_window"] = [
                (event_date - timedelta(days=1)).strftime("%Y-%m-%d"),
                item["date"]
            ]
            
            # 2. Harvest Window (Depends on crop shelf-life)
            # For flowers/jasmine: Harvest 12 hours before.
            # For grains/sugarcane: Harvest 3-5 days before.
            item["harvest_start"] = (event_date - timedelta(days=3)).strftime("%Y-%m-%d")
            
            enriched_data.append(item)
            
        return enriched_data

    @staticmethod
    def filter_by_crop(crop_name):
        """Filters the calendar for a specific crop (e.g., 'Jasmine')."""
        full_data = AgriLogic.get_enriched_calendar()
        return [d for d in full_data if crop_name.lower() in [c.lower() for c in d["crops"]]]

    @staticmethod
    def get_today_status():
        """Checks if today is a 'Red' or 'Yellow' zone."""
        today = datetime.now().strftime("%Y-%m-%d")
        data = AgriLogic.get_enriched_calendar()
        
        for day in data:
            if today == day["date"]:
                return {"status": "PEAK", "msg": f"Today is {day['event']}! Sell now."}
            elif today == day["harvest_start"]:
                return {"status": "PREP", "msg": f"Prepare to harvest for {day['event']}."}
        
        return {"status": "NORMAL", "msg": "Market rates are stable."}