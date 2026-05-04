from sqlalchemy import Column, Boolean, Integer, String, Numeric, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

#===============================#
# DOMAIN-A: Internal Operations #
#===============================#
class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Strict Internal Roles: "Analyst", "Admin"
    role = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)

#===============================#
#  DOMAIN-B: Public Financials  #
#===============================#
class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)

    # Financial Precision
    balance = Column(Numeric(precision=12, scale=2), default = 0.00, nullable=False)
    is_active = Column(Boolean, default=True)

    # Establishing the Relationship: A customer owns multiple records
    records = relationship("Record", back_populates="owner")

#===============================#
#     DOMAIN-C: The Ledger      #
#===============================#
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(precision=12, scale=2), nullable=False)
    record_type = Column(String, nullable=False) # Ex: "income" or "expense"
    category = Column(String, nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    notes = Column(String, nullable=True)

    # CRITICAL FIX: The foreign key is now explicitly linked to the customer table
    customer_id = Column(Integer, ForeignKey("customers.id"))

    # Establishing the reverse relationship back to the customer
    owner = relationship("Customer", back_populates="records")