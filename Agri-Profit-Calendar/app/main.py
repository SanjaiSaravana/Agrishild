import os
import json
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Static and Templates setup
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def get_calendar_data():
    path = os.path.join(BASE_DIR, "data", "calendar_2026.json")
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Map the day number to the full data object for quick HTML lookup
    return {int(item["date"].split("-")[-1]): item for item in data}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    days_lookup = get_calendar_data()
    
    # February 2026 starts on Sunday. Offset = 0 empty slots.
    # We pass 'range(0)' for the offset and the lookup dict to the UI.
    return templates.TemplateResponse("index.html", {
        "request": request, 
        "days_dict": days_lookup,
        "offset": range(0) 
    })