from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PolicyCreate(BaseModel):
    wallet_address: str
    coverage_amount: float = 10.0
    premium_paid: float = 0.5


class PolicyResponse(BaseModel):
    policy_id: str
    wallet_address: str
    coverage_amount: float
    premium_paid: float
    start_date: datetime
    end_date: Optional[datetime]
    is_active: bool

    class Config:
        from_attributes = True


class PayoutCreate(BaseModel):
    policy_id: str
    wallet_address: str
    amount: float
    tx_signature: str
    trigger_type: str
    trigger_value: Optional[str] = None
    confirmed: bool = False
    explorer_url: Optional[str] = None


class PayoutResponse(BaseModel):
    id: int
    policy_id: str
    wallet_address: str
    amount: float
    tx_signature: str
    trigger_type: str
    executed_at: datetime
    confirmed: bool
    explorer_url: Optional[str]

    class Config:
        from_attributes = True
