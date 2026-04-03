from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import user_service

# Starting the Router Instance
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["Authentication"],
)

@router.post("/register", response_model=schemas.UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # 1. Checking if the username already exists in the Vault
    existing_user = db.query(models.User).filter(models.User.username == user.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username is already taken!"
        )
    
    # 2. Handig off the request to Layer-3 (The Brain) to actually crate the user entry
    new_user = user_service.create_user(db=db, user=user)

    return new_user
