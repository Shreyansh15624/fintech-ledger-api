from sqlalchemy.orm import Session
from passlib.context import CryptContext
from app import models, schemas

# Setting up the 'bcrypt Hashing Engine'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_user(db: Session, user: schemas.UserCreate):
    # 1. Hashing the Incoming Plain Text Password
    hashed_pw = get_password_hash(user.password)

    # 2. Create the SQLAlchemy Model Instance
    db_user = models.User(
        username=user.username,
        password_hash=hashed_pw,
        role=user.role
    )

    # 3. Adding to the Database, Committing the Transaction, and refresh to get the ID
    db.add(db_user)
    db.commit()
    db.refresh()

    return db_user