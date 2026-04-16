from sqlalchemy import Column, Integer, String, DateTime, Float, Boolean, Text, ForeignKey, desc
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from .database import Base
import datetime

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String, nullable=True)
    role = Column(String, default="buyer") # 'farmer' or 'buyer'
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# --- Bidding System Models ---

class BiddingUser(Base):
    __tablename__ = "bidding_users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(150), unique=True, nullable=False)
    password = Column(String(150), nullable=False)
    role = Column(String(50), nullable=False)  # 'farmer' or 'bidder'
    
    crops = relationship("Crop", back_populates="farmer", cascade="all, delete-orphan")
    bids = relationship("Bid", back_populates="bidder")
    
    @property
    def is_authenticated(self):
        return True


class Crop(Base):
    __tablename__ = "crops"
    
    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(Integer, ForeignKey("bidding_users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    quantity = Column(String(50), nullable=False)
    base_price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    ai_grade = Column(String(10), nullable=False)
    meet_link = Column(String(200), nullable=True)
    end_time = Column(DateTime, nullable=False)
    
    farmer = relationship("BiddingUser", back_populates="crops")
    bids = relationship("Bid", back_populates="crop", cascade="all, delete-orphan")
    
    def highest_bid(self):
        if self.bids:
            return max([bid.amount for bid in self.bids])
        return 0
    
    def is_active(self):
        return datetime.datetime.now() < self.end_time
    
    def get_winner(self):
        if self.bids and not self.is_active():
            highest = max(self.bids, key=lambda b: b.amount)
            return highest.bidder.username
        return None


class Bid(Base):
    __tablename__ = "bids"
    
    id = Column(Integer, primary_key=True, index=True)
    crop_id = Column(Integer, ForeignKey("crops.id"), nullable=False)
    bidder_id = Column(Integer, ForeignKey("bidding_users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    crop = relationship("Crop", back_populates="bids")
    bidder = relationship("BiddingUser", back_populates="bids")


class AdvisoryFarmer(Base):
    __tablename__ = "advisory_farmers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    city = Column(String, nullable=False)
    crop = Column(String, nullable=False)


class InsurancePolicy(Base):
    __tablename__ = "insurance_policies"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, unique=True, index=True, nullable=False)
    wallet_address = Column(String, nullable=False)
    coverage_amount = Column(Float, nullable=False)  # in SOL
    premium_paid = Column(Float, nullable=False)  # in SOL
    start_date = Column(DateTime(timezone=True), server_default=func.now())
    end_date = Column(DateTime(timezone=True))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class PayoutHistory(Base):
    __tablename__ = "payout_history"

    id = Column(Integer, primary_key=True, index=True)
    policy_id = Column(String, nullable=False)
    wallet_address = Column(String, nullable=False)
    amount = Column(Float, nullable=False)  # in SOL
    tx_signature = Column(String, unique=True, nullable=False)
    trigger_type = Column(String, nullable=False)  # heatwave, drought, crop_failure
    trigger_value = Column(String)
    executed_at = Column(DateTime(timezone=True), server_default=func.now())
    confirmed = Column(Boolean, default=False)
    explorer_url = Column(String)
