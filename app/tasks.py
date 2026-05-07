from app.worker import celery_app
from app.database import SessionLocal
from app.models import Customer, Record
from sqlalchemy.exc import IntegrityError
import time

@celery_app.task(bind=True, name="process_tansfer")
def process_transfer_task(self, sender_id: int, receiver_id: int, amount: float, category: str):
    """
    This task runs completely in the background. FastAPI doesn't wait for this to finish! 
    """
    db = SessionLocal()
    try:
        # 1. Locking the Sender
        sender = db.query(Customer).with_for_update().filter(Customer.id == sender_id).first()
        if not sender or sender.balance < amount:
            return {"status": "failed", "reason": "Insufficient Funds / Invalid Sender!"}

        # 2. Locking the Receiver
        receiver = db.query(Customer).with_for_update().filter(Customer.id == receiver_id).first()

        # 3. Executing the Math
        sender.balance -= amount
        receiver.balance += amount

        # 4. Writing Records to the Ledger
        sender_record = Record(amount=amount, record_type="expense", category=category, customer_id=sender.id)
        receiver_record = Record(amount=amount, record_type="income", category=category, customer_id=receiver.id)

        db.add(sender_record)
        db.add(receiver_record)

        # Committing everything to HardDrive
        db.commit()
        return {"status": "success", "amount_transferred": amount}
    
    except Exception as e:
        db.rollback()
        return {"status": "failed", "reason": str(e)}
    
    finally:
        db.close()