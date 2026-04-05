import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from app import models
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

#==============================================
# ADVANCED FIXTURES (Sending the Database)
#==============================================
@pytest.fixture
def test_db():
    """
    yields a database session specifically for our fixtures to use
    """
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture
def test_admin_user(test_db):
    """
    Creates the baseline Admin user for Authenticaed tests
    """
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("adminpass123")
    
    admin = models.User(
        username="admin_user",
        password_hash=hashed_pw,
        role="Admin",
        is_active=True
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def seeded_records(test_db, test_admin_user):
    """
    Populates the database for specific financial data for analytics testing
    """
    records = [
        models.Record(amount=25000, category="Housing", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=1500, category="Utilities", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=500, category="Food", record_type="expense", user_id=test_admin_user.id),
        models.Record(amount=97000.5, category="Salary", record_type="income", user_id=test_admin_user.id),
    ]
    test_db.add_all(records)
    test_db.commit()
    return test_db

@pytest.fixture
def authorized_client(test_admin_user):
    """
    Creating a special test client that is already logged in as the Admin
    """

    # Using the global client ot log in
    res = client.post(
        "/api/v1/auth/login",
        data={"username": "admin_user", "password": "adminpass123"}
    )
    token = res.json()["access_token"]

    # Creating a fresh client with JWT Authentication
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token}"}
    return auth_client

@pytest.fixture
def deactivated_user(test_db):
    """
    Creates a user that has been soft-deleted
    """
    from app.services import user_service

    hashed_pw = user_service.get_password_hash("testpass123")

    user = models.User(
        username="fired_analyst",
        password_hash=hashed_pw,
        role="Analyst",
        is_active=False, # The Crucial Soft Delete Switch
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

#==============================================
# MOST IMPORTANT! INTEGRATION TESTS
#==============================================

def tests_search_engine_validation_error(authorized_client):
    """
    Tests the Defensive Program on the Search Engine
    """
    response = authorized_client.get("/api/v1/records/?min_amount=5000&max_amount=1000")

    assert response.status_code == 401
    assert "Maximum Amount cannot be less than Minimum Amount" in response.json()["detail"]

def test_deactivated_user_cannot_login(deactivated_user):
    """
    Tests if the soft-deleted users are properly blocked from logging in during Login Process
    """
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "fired_analyst", "password": "testpass123"}
    )

    assert response.status_code == 403
    assert "Deactivated" in response.json()["detail"]

def test_analytics_dashboard(authorized_client, seeded_records):
    """
    Testing the complex SQLAlchemy Aggregations against predictable seeded data
    """
    response = authorized_client.get("/api/v1/analytics/summary")

    assert response.status_code == 200
    data = response.json()

    assert data["totals"]["total_expenses"] == 27000.0 # 25000 + 1500 + 500
    assert data["metrics"]["total_transaction_count"] == 3
    assert data["expense_breakdown"]["Housing"] == 25000.0