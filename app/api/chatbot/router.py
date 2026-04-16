from fastapi import APIRouter, Request
from .service import get_ai_response
from app.api.chatbot.service import get_ai_response
router = APIRouter()

@router.post("/")
async def chat_endpoint(request: Request):
    data = await request.json()
    response = await get_ai_response(data.get("message"), data.get("state"), data.get("history", []))
    return {"reply": response}