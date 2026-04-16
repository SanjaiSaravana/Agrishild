from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from .service import service

router = APIRouter()

class PolicyCheckRequest(BaseModel):
    wallet_address: str

class TriggerCheckRequest(BaseModel):
    lat: float
    lon: float

class PayoutRequest(BaseModel):
    wallet_address: str

@router.post("/policy-status")
async def check_policy(request: PolicyCheckRequest):
    try:
        return await service.get_policy_status(request.wallet_address)
    except Exception as e:
        print(f"Policy status error: {e}")
        return {
            "status": "error",
            "message": str(e),
            "policy_id": "ERROR",
            "pool_balance": "0 SOL"
        }

@router.post("/check-triggers")
async def check_triggers(request: TriggerCheckRequest):
    try:
        return await service.check_triggers(request.lat, request.lon)
    except Exception as e:
        print(f"Trigger check error: {e}")
        return {
            "payout_eligible": False,
            "payout_amount": 0,
            "triggers": [],
            "error": str(e)
        }

@router.post("/payout")
async def process_payout(request: PayoutRequest):
    try:
        return await service.process_payout(request.wallet_address)
    except Exception as e:
        print(f"Payout error: {e}")
        return {
            "success": False,
            "message": f"Payout failed: {str(e)}"
        }
