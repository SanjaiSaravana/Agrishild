from fastapi import APIRouter, UploadFile, File, HTTPException
from .service import predict_disease

router = APIRouter()

@router.post("/predict")
async def predict(image: UploadFile = File(...)):
    if not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File provided is not an image.")
    
    try:
        contents = await image.read()
        result = await predict_disease(contents)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
