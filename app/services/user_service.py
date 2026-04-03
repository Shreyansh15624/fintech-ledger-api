import bcrypt
from sqlalchemy.orm import Session
from app import models, schemas

def get_password_hash(password: str) -> str:
    # 'brcypt' requires raw bytes
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
    db.refresh(db_user)

    return db_user