import concurrent.futures
from app import models

# 1. Testing for the Health Check
def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200

# 2. Testing the Security Perimeter (Unauthorized Access)
def test_unauthorized_records_access(client):
    # Trying to get records without a token
    response = client.get("/api/v1/records")
    assert response.status_code == 401

def test_full_auth_and_record_flow(client):
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

    res_record = client.post("/api/v1/records", json=record_data, headers=headers)
    assert res_record.status_code == 201
    assert res_record.json()["amount"] == '5000.00'

# 3. Testing the Pydantic Validation Logic
def test_pydantic_validation_blocks_bad_data(client):
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
    response = client.post("/api/v1/records/", json=bad_data, headers=headers)
    assert response.status_code == 422

def tests_search_engine_validation_error(authorized_client):
    """
    Tests the Defensive Program on the Search Engine
    """
    response = authorized_client.get("/api/v1/records/?min_amount=5000&max_amount=1000")

    assert response.status_code == 401
    assert "Maximum Amount cannot be less than Minimum Amount" in response.json()["detail"]

def test_deactivated_user_cannot_login(client, deactivated_user):
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

def test_pessimistic_lock_prevents_double_spend(authorized_client, test_db, test_admin_user):
    """
    Stress test for the /transfer endpoint to ensure pessimistic locking (FOR UPDATE)
    prevents race conditions and double-spending under concurrent load.
    """
    # 1. SETUP: Funding User A & Creating User B
    # Granting the Exisitng test_admin_user $500 to start
    test_admin_user.balance = 500.00

    # Creating the receiver (User B) with a starting balance of $0
    receiver = models.User(
        username="receiver_user",
        password_hash="dummyhash",
        role="Analyst",
        balance=0.00,
    )
    test_db.add(receiver)
    test_db.commit()
    test_db.refresh(receiver)

    sender_id = test_admin_user.id
    receiver_id = receiver.id

    # 2. THE COLLISION COURSE:
    # Payload 1 wants $400 & Payload 2 wants $300.
    # Total request is $700, but the balance is only $500.
    payload_1 = {"sender_id": sender_id, "receiver_id": receiver_id, "amount": 400.00}
    payload_2 = {"sender_id": sender_id, "receiver_id": receiver_id, "amount": 300.00}

    # Helper function to fire the authenticated request
    def fire_transfer(payload):
        # Authorized client automatically injects the Bearer token
        return authorized_client.post("/api/v1/records/transfer", json=payload)
    
    # 3. THE STRESS TEST: Firing both the requests at the exact smae millisecond!
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(fire_transfer, payload_1)
        future2 = executor.submit(fire_transfer, payload_2)

        response1 = future1.result()
        response2 = future2.result()
    
    # 4. THE VERDICT: Checking the Status Codes
    status_codes = [response1.status_code, response2.status_code]

    # Checking to see if exactly one transaction absolutely succeed & one failed!
    assert 200 in status_codes
    assert 400 in status_codes

    # 5. THE LEDGER AUDIT: Verify if the final database state is mathematically pure
    test_db.refresh(test_admin_user)
    test_db.refresh(receiver)

    # Now regardless of which transaction won the race here, the total money within the system must remain exactly $500
    assert float(test_admin_user.balance) + float(receiver.balance) == 500.00

    # The sender's balance must be exactly $100 or $200 depending on which request won
    assert float(test_admin_user.balance) in {100.00, 200.00}