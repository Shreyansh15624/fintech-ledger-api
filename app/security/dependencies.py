from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.security import jwt_handler

# Dual Auth Entry Points for the Swagger UI
oauth2_employee_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/employee/login")
oauth2_customer_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/customer/login")

def get_current_employee(token: str = Depends(oauth2_employee_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate Employee Credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, jwt_handler.SECRET_KEY, algorithms=[jwt_handler.ALGORITHM])
        username: str = payload.get("sub")
        account_type: str = payload.get("type")
        if username is None or account_type != "employee":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    employee = db.query(models.Employee).filter(models.Employee.username == username).first()
    if employee is None:
        raise credentials_exception
    return employee

def get_current_customer(token: str = Depends(oauth2_customer_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate Customer Credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, jwt_handler.SECRET_KEY, algorithms=[jwt_handler.ALGORITHM])
        username: str = payload.get("sub")
        account_type: str = payload.get("type")
        if username is None or account_type != "customer":
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    customer = db.query(models.Customer).filter(models.Customer.username == username).first()
    if customer is None:
        raise credentials_exception
    return customer

class RoleChecker:
    def __init__(self, allowed_roles: set):
        self.allowed_roles = allowed_roles
    
    def __call__(self, employee: models.Employee = Depends(get_current_employee)):
        if employee.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You lack the required privileges to perform this action!",
            )
        return employee