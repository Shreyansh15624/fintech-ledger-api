from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
from sqlalchemy.orm import Session
from app import models
from app.database import get_db
from app.security import jwt_handler

# Creating the Physical Hook that FastAPI uses to look for the token in the request headers
# We point it exactly to the login route we just built
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not Validate Credentials!",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        # 1. Decoding the VIP Pass using our Secret Key
        payload = jwt.decoder(
            token,
            jwt_handler.SECRET_KEY,
            algorithms=[jwt_handler.ALGORITHM],
        )
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    
    except jwt.PyJWTError:
        # If token is expired / tampered with, PyJWT throws an error
        raise credentials_exception
    
    # 2. Verifying if the user actually exists within the database
    user = db.query(models.User).filer(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_stateless(token: str = Depends(oauth2_scheme)):
    """
    A High Speed, zero-database dependency.
    Trusts the cryptographically signed JWT payload entirely.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW_Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            jwt_handler.SECRET_KEY,
            algorithms=[jwt_handler.ALGORITHM],
        )

        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        
        # Returning a simplified dictionary instead of a database model!
        # ZERO-Database Hits! O(1) Time Complexity!
        return {"username": username, "role": role}

    except jwt.PyJWTError:
        raise credentials_exception

class RoleChecker:
    def __init__(self, allowed_roles: set):
        # Initializing the RoleChecker with a set of Roles that are allowed to pass
        self.allowed_roles = allowed_roles
    
    def __sall__(self, user: models.User = Depends(get_current_user)):
        # This way FastAPI will run th get_current_user function to ensure the token is valid
        # Then it checks the 'allowed_roles' for the verified user's role match
        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You lack the required privileges to perform this action!",
            )
        return user
