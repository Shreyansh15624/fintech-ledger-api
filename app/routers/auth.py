from urllib.parse import scheme_chars
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app import schemas, models
from app.database import get_db
from app.services import user_service
from fastapi.security import OAuth2PasswordRequestForm
from app.security import jwt_handler
from datetime import timedelta

# Starting the Router Instance
router = APIRouter()

# ------- EMPLOYEE AUTH -------
@router.post("/employee/register", response_model=schemas.EmployeeResponse, status_code=status.HTTP_201_CREATED)
def register_employee(employee: schemas.EmployeeCreate, db: Session = Depends(get_db)):
    if db.query(models.Employee).filter(models.Employee.username == employee.username).first():
        raise HTTPException(status_code=400, detail="Username taken!")
    return user_service.create_employee(db=db, employee=employee)


@router.post("/employee/login")
def login_employee(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    employee = db.query(models.Employee).filter(models.Employee.username == form_data.username).first()
    if not employee or not employee.is_active or not user_service.verify_password(form_data.password, employee.password_hash):
        user_service.dummy_verify()
        raise HTTPException(status_code=401, detail="Invalid Credentials / Deactivated Account")
    

    token = jwt_handler.create_access_token(
        data={"sub": employee.username, "role": employee.role, "type": "employee"},
        expires_delta=timedelta(minutes=jwt_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}

# ------- CUSTOMER AUTH -------
@router.post("/customer/register", response_model=schemas.CustomerResponse, status_code=status.HTTP_201_CREATED)
def register_customer(customer: schemas.CustomerCreate, db: Session = Depends(get_db)):
    if db.query(models.Customer).filter(models.Customer.username == customer.username).first():
        raise HTTPException(status_code=400, details="Username taken!")
    return user_service.create_customer(db=db, customer=customer)

@router.post("/customer/login")
def login_customer(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    customer = db.query(models.Customer).filter(models.Customer.username == form_data.username).first()
    if not customer or not customer.is_active or not user_service.verify_password(form_data.password, customer.password_hash):
        user_service.dummy_verify()
        raise HTTPException(status_code=401, detail="Invalid Credential / Deactivated Account")
    
    token = jwt_handler.create_access_token(
        data={"sub": customer.username, "role": "None", "type": "customer"},
        expires_delta=timedelta(minutes=jwt_handler.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token, "token_type": "bearer"}