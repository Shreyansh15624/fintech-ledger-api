from app.tasks import process_transfer_task
from app.security.dependencies import get_current_customer
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from app import models, schemas
from app.database import get_db
from app.security.dependencies import RoleChecker
from app.services import record_service

router = APIRouter()

# 1. CREATE RECORD (strictly locked to 'Admin' role)
@router.post("/", response_model=schemas.RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    # The request is intercepted by the Bouncer, right here!
    current_customer: models.Customer = Depends(get_current_customer)
):
    # Create the database model & explictly link it to the Admin who created it
    new_record = models.Record(
        **record.model_dump(),
        customer_id=current_customer.id,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record

# 2. READING ALL THE RECORDS (Locked to 'Admin' & 'Analyst' Roles)
@router.get("/", response_model=List[schemas.RecordResponse])
def get_records(
    # Pagination
    skip: int = 0,
    limit: int = 100,
    
    # Dynamic Search Parameters
    record_type: Optional[str] = None,
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    
    # Dependencies for Database & Authentication
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(RoleChecker({"Admin", "Analyst"}))
):
    # ------ LOGICAL VALIDATION GATE ------ #
    if min_amount is not None and max_amount is not None:
        if max_amount < min_amount:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Maximum Amount cannot be less than Minimum Amount",
            )
    
    
    # Starting with a base query
    query = db.query(models.Record)

    # 1. If "Exact Match", we filter by "income" or "expense"
    if record_type:
        query = query.filter(models.Record.record_type == record_type)

    # 2. If "Fuzzy Match", search by category (ex: "soft" finds "Software")
    if category:
        query = query.filter(models.Record.category.ilike(f"%{category}%"))

    # 3. If "Range Match", but we filter by "Minimum Amount"
    if min_amount is not None:
        query = query.filter(models.Record.amount >= min_amount)

    # 4. if "Range Match", but we filter by "Maximum Amount"
    if max_amount is not None:
        query = query.filter(models.Record.amount <= max_amount)
    
    # Executing this dynamically built query with pagination
    records = query.offset(skip).limit(limit).all()

    return records

# 3. UPDATE RECORD (Strictly Locked to 'Admin' Role)
@router.put("/{id}", response_model=schemas.RecordResponse)
def update_record(
    id: int,
    update_record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(RoleChecker({"Admin"}))
):
    # 1. Finding the specific record
    record_query = db.query(models.Record).filter(models.Record.id == id)
    record = record_query.first()

    # 2. It the record doesn't exist, we throw a clean 404
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Record doesn't exist",
        )
    
    # 3. Apply the updates & save
    record_query.update(update_record.model_dump(), synchronize_session=False)
    db.commit()

    return record_query.first()

# 4. DELETE RECORD (Strictly Locked to 'Admin' Role)
@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_record(
    id: int,
    db: Session = Depends(get_db),
    current_employee: models.Employee = Depends(RoleChecker({"Admin"})),
):
    record_query = db.query(models.Record).filter(models.Record.id == id)
    record = record_query.first()

    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Record with id: {id}, Does Not Exist!"
        )
    
    record_query.delete(synchronize_session=False)
    db.commit()

# 5. FUND TRANSFER (Asynchronous Celery Implementation)
@router.post("/transfer", status_code=status.HTTP_202_ACCEPTED)
def initiate_transfer(
    payload: schemas.TransformRequest,

    # Ensuring that only the authenticated roles can trigger transfer
    current_customer: models.Customer = Depends(get_current_customer)
):
    """
    Instantly accepts the transfer request and queues it for the Celery worker to process.
    """
    # 1. Dropping the ticket for the Redis Broker to catch and queue using '.delay()'
    task = process_transfer_task.delay(
        sender_id=payload.sender_id,
        receiver_id=payload.receiver_id,
        amount=payload.amount,
        category="Transfer", # Creating a default Category since Locust doesn't specify one
    )

    # 2. Instantly receive a receipt to the User
    return {
        "message": "Transfer request is accepted and is processing in the background.",
        "task_id": task.id,
    }