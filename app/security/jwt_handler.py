from datetime import datetime, timedelta, timezone
import jwt
from typing import Optional
import os

# In a real Production App, this never get's Hardcoded!
# Its only hardcoded because this is an Assignment!
SECRET_KEY = os.environ.get("JWT_SECRET", "zorvyn_super_secret_key_for_assessment_only")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})

    # This step is what creates the hashed token string
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

