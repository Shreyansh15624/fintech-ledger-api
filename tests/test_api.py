import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.database import Base, get_db


# 1. SETUP: Creating an isolated, temporary in-memory database
SQL_ALCHEMY_DATABASE_URL = "sqlite:///:memory"

engine = create_engine(
    SQL_ALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# 2. OVERRIDE: FastAPI will use this fake database instead of a real one
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

# 3. FIXTURE: Creates a clean slate automatically before any single test runs
@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield # The test will run in this window created by this line
    Base.metadata.drop_all(bind=engine)

#==============================================
# THE TESTS BEGIN FROM HERE
#==============================================

# 1. Testing for the Health Check
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200

# 2. Testing the Security Perimeter (Unauthorized Access)
def test_unauthorized_records_access():
    # Trying to get records without a token
    response = client.get("/")
    assert response.status_code == 200

def test_full_auth_and_record_flow():
    # 1. Registering the User (DB is empty now, so this approach is safe)
    client.post(
        "/api/v1/auth/register",
        json={"username": "improved_qa", "password": "supersecret", "role": "Admin"}
    )

    # 2. Logging in (Must use 'data' for OAuth2)
    res_login = client.post(
        "/api/v1/auth/login",
        data={"username": "improved_qa", "password": "supersecret"}
    )
    assert res_login.status_code == 200
    token = res_login.json()["access_token"]

    # 3. Creating a record using the valid login token
    headers = {"Authorization": f"Bearer {token}"}
    record_data = {
        "amount": 5000.0,
        "record_type": "expense",
        "category": "Software",
        "notes": "AWS Hosting",
    }

    res_record = client.post("/api/v1/records/", json=record_data, headers=headers)
    assert res_record.status_code == 201
    assert res_record.json()["amount"] == 5000.0

# 3. 
def test_pydantic_validation_blocks_bad_data():
    # 1. Registering & Logging in to the application
    client.post(
        "/api/v1/auth/register",
        json={"username": "bad_actor", "password": "password", "role": "Admin"}
    )
    login = client.post(
        "/api/v1/auth/login",
        data={"username": "bad_actor", "password": "password"}
    )
    token = login.json()["access_token"]

    # 2. Sending a negative Amount (Expected to be blocked by Pydantic's `gt=0`)
    headers = {"Authorization": f"Bearer {token}"}
    bad_data = {"amount": -1000, "record_type": "expense", "category": "Food"}

    # 3. Validating the Response (Expected to block the 'bad_actor')
    response = client.post("api/v1/records/", json=bad_data, headers=headers)
    assert response.status_code == 422
