from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter(
    prefix="/api/v1/records",
    tags=["Financial Records"],
)

# 1. CREATE RECORD (strictly locked to 'Admin' role)
@router.post("/", response_model=schemas.RecordResponse, status_code=status.HTTP_201_CREATED)
def create_record(
    record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    # The request is intercepted by the Bouncer, right here!
    current_user: models.User = Depends(RoleChecker({"Admin"}))
):
    # Create the database model & explictly link it to the Admin who created it
    new_record = models.Record(
        **record.model_dump(),
        user_id=current_user.id,
    )
    db.add(new_record)
    db.commit()
    db.refresh(new_record)

    return new_record

# 2. READING ALL THE RECORDS (Locked to 'Admin' & 'Analyst' Roles)
@router.get("/", response_model=List[schemas.RecordResponse])
def get_records(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker({"Admin", "Analyst"}))
):
    # Querying the dataset for all the records
    records = db.query(models.Record).offset(skip).limit(limit).all()
    return records

# 3. UPDATE RECORD (Strictly Locked to 'Admin' Role)
@router.put("/{id}", response_model=schemas.RecordResponse)
def update_record(
    id: int,
    update_record: schemas.RecordCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(RoleChecker({"Admin"}),)
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
    current_user: models.User = Depends(RoleChecker({"Admin"})),
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