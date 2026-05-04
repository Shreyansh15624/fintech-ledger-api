from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app import models, schemas

def execute_transfer(db: Session, transfer: schemas.TransferRequest):
    # Precaution: Preventing Transfering to oneself
    if transfer.sender_id == transfer.receiver_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot transfer funds to the same account."
        )
    
    # 1. DETERMINISTIC LOCKING ORDER (The deadlock killer)
    # Lock the lowest ID first, regardless of who is the sender / receiver
    first_lock_id, second_lock_id = sorted([transfer.sender_id, transfer.receiver_id])

    try:
        # 2. Locking the first row
        account_1 = db.query(models.User).filter(models.User.id == first_lock_id).with_for_update().first()
        if not account_1:
            raise HTTPException(
                status_code=404,
                detail=f"Account {first_lock_id} not found!",
            )
        
        # 3. Locking the 2nd row
        account_2 = db.query(models.User).filter(models.User.id == second_lock_id).with_for_update().first()
        if not account_2:
            raise HTTPException(
                status_code=404,
                detail=f"Account {second_lock_id} not found!",
            )
        
        # 4. Mapping the locked roles back to their actual roles 
        sender = account_1 if account_1.id == transfer.sender_id else account_2
        receiver = account_2 if account_1.id == transfer.sender_id else account_1

        # 5. Business Logic Validation (100% Safe from race conditions)
        # Note: This assumes that the User model already has a 'balance' float / integer column in place
        if sender.balance < transfer.amount:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient Funds for Transfer.",
            )

        # 6. Mutating each of the account's balance based on the transfer amount
        sender.balance -= transfer.amount
        receiver.balance += transfer.amount

        # 7. Creating the immutable Ledger Records for the audit trail
        outbound_record = models.Record(
            user_id=sender.id,
            amount=-transfer.amount,
            notes=f"Transfer to user {receiver.id}",
            record_type="expense",
            category="transfer",
        )

        inbound_record = models.Record(
            user_id=receiver.id,
            amount=transfer.amount,
            notes=f"Transfer from user {sender.id}",
            record_type="income",
            category="transfer",
        )

        db.add(outbound_record)
        db.add(inbound_record)

        # 8. Committing the changes, whcih also releases the locks!
        db.commit()

        return {"status": "success", "tx_amount": transfer.amount, "sender_new_balance": sender.balance}
    
    except HTTPException:
        # If its an API Error that was explicitly raised, roll back and pass it up!
        db.rollback()
        raise

    except Exception as e:
        # If the database crashes / the connection drops, ROLLBACK is critical to free the locks
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error {e}: Transaction Failed! Locks released!",
        )