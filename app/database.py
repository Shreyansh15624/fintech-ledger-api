import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from dotenv import load_dotenv

# 1. Loading the secrets from the '.env' file into the system environment!
load_dotenv()

# 2. Fetching the secure URL dynamically
db_user = os.getenv("POSTGRES_USER")
db_pass = os.getenv("POSTGRES_PASSWORD")
db_name = os.getenv("POSTGRES_DB")

# If DATABASE_URL isn't set, then we default to the localhost for the local development outside of Docker 
db_host = os.getenv("POSTGRES_HOST", "127.0.0.1")

SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_pass}@{db_host}:5432/{db_name}"

# A failsafe to prevent the app from booting at all if the '.env' file is missing
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("⚠️CRITICAL: DATABASE_URL Environment Variable is Missing!")

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_timeout=30.0,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# This is the dependency injection. It gives our routers a database session & safely closes it
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
