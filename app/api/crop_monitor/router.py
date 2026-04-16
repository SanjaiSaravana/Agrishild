from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .service import analyze_crop_health

router = APIRouter()

class AnalysisRequest(BaseModel):
    lat: float
    lon: float

@router.post("/analyze")
async def analyze_endpoint(request: AnalysisRequest):
    try:
        result = await analyze_crop_health(request.lat, request.lon)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
