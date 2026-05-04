from pydantic import BaseModel, Field, PositiveFloat
from typing import List, Dict, Optional, Literal
from datetime import datetime
from decimal import Decimal
#===========================#
# Building the User Schemas #
#===========================#

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    role: Literal["Viewer", "Analyst", "Admin"] = "Viewer"

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool
    
    # Telling Pydantic to read Data even if its not a 'dict()', but an 'ORM Model'
    model_config = {"from_attributes": True}

#==============================#
# Building the Record  Schemas #
#==============================#

class RecordCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount must strictly be positive!")
    record_type: Literal["income", "expense"] = Field(..., description="Strictly 'income' or 'expense'")
    category: str = Field(..., min_length=2)
    notes: Optional[str] = None

class RecordResponse(RecordCreate):
    id: int
    date: datetime
    user_id: int

    model_config = {"from_attributes": True}

class TransferRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: Decimal = Field(gt=0, description="Amount must be strictly positive!")

#========================================#
# Building the Analytics Payload Schemas #
#========================================#

class TotalSchema(BaseModel):
    income: int
    expense: int
    net_balance: int

class MetricsSchema(BaseModel):
    total_transaction_count: int
    average_expese_value: float

class TopExpenseSchema(BaseModel):
    category: str
    amount: float

class FinancialSummaryResponse(BaseModel):
    totals: TotalSchema
    metrics: MetricsSchema
    expense_breakdown: Dict[str, float]
    top_expenses: List[TopExpenseSchema]