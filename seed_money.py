from app.database import SessionLocal
from app.models import Customer
from passlib.context import CryptContext

# A pre-calculated bcrypt hash for the literal string: "password"
# The Locust must use the password "password" to log in!
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def seed():
    # Open a session using the dependency you built in database.py
    db = SessionLocal()
    try:
        # 1. Check if the load_tester already exists
        customer = db.query(Customer).filter(Customer.username == "load_tester").first()
        
        if not customer:
            # 2. Inject the whole user profile if they are missing
            customer = Customer(
                username="load_tester",
                password_hash=pwd_context.hash("password"),
                balance=1000000.00,
                is_active=True
            )
            db.add(customer)
            print("Injected new 'load_tester' account with $1,000,000!")
        else:
            # 3. Just top up the money if they already exist
            customer.balance = 1000000.00
            print("Account found. Balance topped up to $1,000,000!")
            
        # Commit the transaction to the database
        db.commit()
    finally:
        db.close()

if __name__ == "__main__":
    seed()