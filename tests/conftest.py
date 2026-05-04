import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app import models
from app.main import app
from app.database import Base, get_db

# 1. SETUP: Creating an In-Memory DB
SQL_ALCHEMY_DATABASE_URL = "postgresql://ledger_admin:abc123@127.0.0.1:5433/fintech_ledger_test"

engine = create_engine(SQL_ALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----- DOMAIN-A: Employee Fixtures -----
@pytest.fixture
def test_admin_employee(test_db):
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("adminpass123")

    admin = models.Employee(
        username="admin_user",
        password_hash=hashed_pw,
        role="Admin",
        is_active=True,
    )
    test_db.add(admin)
    test_db.commit()
    test_db.refresh(admin)
    return admin

@pytest.fixture
def deactivated_employee(test_db):
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("testpass123")
    user = models.Employee(
        username="fired_analyst",
        password_hash=hashed_pw,
        role="Analyst",
        is_active=False,
    )
    test_db.add(user)
    test_db.commit()
    test_db.refresh(user)
    return user

@pytest.fixture
def authorized_client(client, test_admin_employee):
    res = client.post(
        "/api/v1/auth/employee/login", # Updated to the strict endpoint
        data={"username": "admin_user", "password": "adminpass123"},
    )
    token = res.json()["access_token"]
    auth_client = TestClient(app)
    auth_client.headers = {"Authorization": f"Bearer {token}"}
    return auth_client

# ----- DOMAIN-B: CUSTOMER FIXTURES -----
@pytest.fixture
def test_customer(test_db):
    from app.services import user_service
    hashed_pw = user_service.get_password_hash("customerpass")

    customer = models.Customer(
        username="primary_customer",
        password_hash=hashed_pw,
        balance=500.00,
        is_active=True, 
    )
    test_db.add(customer)
    test_db.commit()
    test_db.refresh(customer)
    return customer

@pytest.fixture
def customer_client(client, test_customer):
    res = client.post(
        "/api/v1/auth/customer/login", # Updated to the strict endpoint
        data={"username": "primary_customer", "password": "customerpass"}
    )
    token = res.json()["access_token"]
    cust_client = TestClient(app)
    cust_client.headers = {"Authorization": f"Bearer {token}"}
    return cust_client

@pytest.fixture
def seeded_records(test_db, test_customer):
    # Records now belong exclusively to customers and not employees
    records = [
        models.Record(amount=25000, category="Housing", record_type="expense", customer_id=test_customer.id),
        models.Record(amount=1500, category="Utilities", record_type="expense", customer_id=test_customer.id),
        models.Record(amount=500, category="Food", record_type="expense", customer_id=test_customer.id),
        models.Record(amount=97000.5, category="Salary", record_type="income", customer_id=test_customer.id),
    ]
    test_db.add_all(records)
    test_db.commit()
    return test_db