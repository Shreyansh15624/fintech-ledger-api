from sqlalchemy import Column, Boolean, Integer, String, Float, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    
    # Strict roles enforcement: "Viewer, Analyst, Admin"
    role = Column(String, default="Viewer", nullable=False)
    
    # FIX-1: Precision mapping for currency (12 digits total, 2 decimal places max)
    # FIX-2: Defaulting to 0.0, so the user registration doesn't crash
    balance = Column(Numeric(precision=12, scale=2), default=0.0, nullable=False)

    # Establishig the relationship: A user can own multiple records
    records = relationship("Record", back_populates="owner")

    # A Soft Delete Parameter
    is_active = Column(Boolean, default=True)

class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)

    # Upgrading the record amount to match the exact precision of the user balance
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    
    record_type = Column(String, nullable=False) # Ex: "income" or "expense"
    category = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(String, nullable=True)

    # The Foreign Key is linking this record directly to a specific user
    user_id = Column(Integer, ForeignKey("users.id"))

    # Establishing the reverse relationship back to the user
    owner = relationship("User", back_populates="records")