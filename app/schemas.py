from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone_number: Optional[str] = None
    role: Optional[str] = "buyer"

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Bidding Schemas ---

class BidBase(BaseModel):
    crop_id: int
    amount: float

class BidCreate(BidBase):
    pass

class Bid(BidBase):
    id: int
    bidder_id: int
    timestamp: datetime

    class Config:
        from_attributes = True

class CropBase(BaseModel):
    name: str
    quantity: str
    base_price: float
    description: Optional[str] = None
    end_time: datetime

class CropCreate(CropBase):
    pass

class Crop(CropBase):
    id: int
    farmer_id: int
    ai_grade: str
    meet_link: Optional[str] = None
    created_at: datetime
    highest_bid: Optional[float] = 0

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None
