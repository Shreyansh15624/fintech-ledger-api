import uuid
from locust import HttpUser, task, between

class FinTechStressTest(HttpUser):
    # Simulates realistic wait times between user clicks (1 to 2 seconds)
    wait_time = between(1, 2)

    def on_start(self):
        """
        Phase-A: The Boot up
        Every virtual user must login to get a JET Token before attacking.
        """
        # Note: We will assume a user named 'load_tester' with a password 'password' exists in the DB
        login_response = self.client.post(
            "/api/v1/auth/customer/login",
            data={"username": "load_tester", "password": "password"},
        )

        if login_response.status_code == 200:
            token = login_response.json().get("access_token")
            # Attach the JWT session so all future requests are authenticated
            self.client.headers.update({"Authorization": f"Bearer {token}"})
        else:
            print("Failed to Login! Make sure that the load_tester account exists!")
    
    @task
    def execute_stress_transfer(self):
        """
        Phase-B & C: The attack and the shield bypass
        """

        # 1. Generate a completely random Idempotency-Key for every single request
        # This forces the Redis cache to register a "Miss" and pass the request to PostgreSQL
        dynamic_headers = {
            "Idempotency-Key": str(uuid.uuid4())
        }

        # 2. Fire the transfer request.
        # Note: We assume the receiver ID-2 exists in the DB
        payload = {
            "sender_id": 1,     # Assuming the Load tester is ID-1
            "receiver_id": 2,   # Sending to a dummy receiver 
            "amount": 1.00      # Small amount to prevent immdetiate empty balances
        }

        # 3. Locust can autmoatically track if this returns a 200 OK / the 500 Internal Error
        self.client.post("/api/v1/records/transfer", json=payload, headers=dynamic_headers)