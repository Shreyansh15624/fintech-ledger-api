from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal
from datetime import datetime
from decimal import Decimal

#================================#
# DOMAIN-A: Employees (Internal) #
#================================#
class EmployeeCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)
    role: Literal["Analyst", "Admin"]

class EmployeeResponse(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}

#================================#
# DOMAIN-B: Customers (External) #
#================================#
class CustomerCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6, max_length=72)

class CustomerResponse(BaseModel):
    id: int
    username: str
    balance: Decimal
    is_active: bool

    model_config = {"from_attributes": True}

#================================#
#   DOMAIN-C: Ledger (Records)   #
#================================#
class RecordCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="Amount must strictly be postive!")
    record_type: Literal["income", "expense"] = Field(..., description='Strictly "income" or "expense".')
    category: str = Field(..., min_length=2)
    notes: Optional[str] = None

class RecordResponse(RecordCreate):
    id: int
    date: datetime
    customer_id: int

    model_config = {"from_attributes": True}

class TransformRequest(BaseModel):
    sender_id: int
    receiver_id: int
    amount: Decimal = Field(gt=0, description="Amount must be strictly positive!")

#================================#
#    Analytics Payload Schema    #
#================================#
class TotalSchema(BaseModel):
    income: Decimal
    expense: Decimal
    net_balance: Decimal

class MetricsSchema(BaseModel):
    total_transaction_count: int
    average_expense_value: Decimal

class TopExpenseSchema(BaseModel):
    category: str
    amount: Decimal

class FinancialSummaryResponse(BaseModel):
    totals: TotalSchema
    metrics: MetricsSchema
    expense_breakdown: Dict[str, Decimal]
    top_expenses: List[TopExpenseSchema]