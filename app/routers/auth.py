from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import user_service
from fastapi.security import OAuth2PasswordRequestForm
from app.security import jwt_handler
from datetime import timedelta
from app.security.dependencies import get_current_user, get_current_user_stateless

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
    
    # 2. Handing off the request to Layer-3 (The Brain) to actually create the user entry
    new_user = user_service.create_user(db=db, user=user)

    return new_user

@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # 1. To find the user in the database by their username!
    user = db.query(models.User).filter(models.User.username ==form_data.username).first()
    if not user:
        # MITIGATION: Running our custom fake hash so the server takes the exact same amount
        # of time, masking whether the username actually exists or not
        user_service.dummy_verify()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )
    
    # 2. To verify the Password's match to the Hash
    if not user_service.verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Credentials",
        )
    
    # 3. Generate the JWT Token
    # We embed both the username & the role into the token payload
    access_token_expires = timedelta(minutes=jwt_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    token_payload = {
        "sub": user.username,
        "role": user.role,
    }

    access_token = jwt_handler.create_access_token(
        data=token_payload, expires_delta=access_token_expires
    )

    # 4. Returning the strict format OAuth2 expects
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user_stateless)):
    # This route is strictly protected, if there's no token / a bad token, the
    # Dependency blocks it and it will never run!
    return {"status": "Access Granted", "user_data": current_user}