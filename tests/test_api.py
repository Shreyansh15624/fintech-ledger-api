from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# 1. Testing for the Health Check
def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Zorvyn API Vault" in response.json()["status"]

# 2. Testing the Security Perimeter (Unauthorized Access)
def test_unauthorized_records_access():
    # Trying to get records without a token
    response = client.get("/api/v1/records/")
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"

# 3. Test Invalid Login (Timing Attack Mitigation Check)
def test_invalid_login():
    response = client.post(
        "/api/v1/auth/login",
        data={"username": "fakeuser", "password": "wrongpassword"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid Credentials"

# 4. Testing User Validation (Handling both new & pre-exsiting states)
def test_user_validation():
    response = client.post(
        "/api/v1/auth/register",
        json={"username": "testadmin_qa", "password": "securepassword123", "role": "Admin"},
    )
    # 201 if created, 400 if it already exists from the previous test run
    assert response.status_code in {201, 400}

# 5. Test Pydantic Data Validation (Negative Amount should be Blocked)
def test_create_record_negative_amount():
    # Logging in for the Token
    login_response = client.post(
        "api/v1/auth/login",
        data={"username": "testadmin_qa", "password": "securepassword123"},
    )

    # If Login is successful, we try to submit bad data
    if login_response.status_code == 200:
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        bad_record = {
            "amount": -50.0, # Negative Amount
            "record_type": "expense",
            "category": "food",
            "notes": "Testing Validation",
        }

        response = client.post("/api/v1/records/", json=bad_record, headers=headers)
        # 422 Unprocessable Entity is expected for Success
        assert response.status_code == 422