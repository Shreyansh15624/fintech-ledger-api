from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import Literal

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
    
    # Telling Pydantic to read Data even if its not a 'dict()', but an 'ORM Model'
    model_config = {"from_attributes": True}

#==============================#
# Building the Record  Schemas #
#==============================#

class RecordCreate(BaseModel):
    amount: float = Field(..., gt=0, description="Amount must strictly be positive!")
    record_type: str = Field(..., description="Must be either 'income' or 'expense'")
    category: str = Field(..., min_length=2)
    notes: Optional[str] = None


class RecordResponse(RecordCreate):
    id: int
    date: datetime
    user_id: int

    model_config = {"from_attributes": True}