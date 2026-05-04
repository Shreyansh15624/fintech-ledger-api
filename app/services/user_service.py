import bcrypt
from sqlalchemy.orm import Session
from app import models, schemas

def get_password_hash(password: str) -> str:
    # 'brcypt' requires raw bytes & we are going to be truncating it to 72 bytes so we can
    # prevent bcrypt crashes / DoS Attacks
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password=pwd_bytes, salt=salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_bytes = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password=password_byte_enc, hashed_password=hashed_password_bytes)

def dummy_verify():
    # A Custom Timing Attack Mitigation.
    # We basically waste the exact amount of time it takes to hash a password
    bcrypt.hashpw(b"dummy_password", bcrypt.gensalt())

def create_employee(db: Session, employee: schemas.EmployeeCreate):
    hashed_pw = get_password_hash(employee.password)
    db_employee = models.Employee(username=employee.username, password_hash=hashed_pw, role=employee.role)
    db.add(db_employee)
    db.commit()
    db.refresh(db_employee)
    return db_employee

def create_customer(db: Session, customer: schemas.CustomerCreate):
    hashed_pw = get_password_hash(customer.password)
    db_customer = models.Customer(username=customer.username, password_hash=hashed_pw)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    return db_customer