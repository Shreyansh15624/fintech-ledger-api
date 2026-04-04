from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter(
    prefix="/api/v1/analytics",
    tags=["Analytics Dashboard"],
)

# SUMMARY ENDPOINT (Locked to Admin & Analyst Roles)
@router.get("/summary")
def get_financial_summary(
    db: Session = Depends(get_db),
    # Limit the privileges to 'Analyst' & 'Admin' roles
    current_user: models.User = Depends(RoleChecker({"Analyst", "Admin"}))
):
    # 1. Asking SQLit to add up all the 'income' records
    total_income = db.query(func.sum(models.Record.amount)).filter(
        models.Record.record_type == "income"
    ).scalar() or 0.0 # We use a `or 0.0` just in case there are no records yet, so it doesn't return None
    # .scalar() pulls the single calculated number out of the query result

    # 2. Asking SQLite to add up all the 'expense' records
    total_expenses = db.query(func.sum(models.Record.amount)).filter(
        models.Record.record_type == "expense"
    ).scalar() or 0.0

    # 3. Calculating the net balance on the server
    net_balance = total_income - total_expenses

    # 4. Return the clean JSON Package to the frontend
    return {
        "total_income": total_income,
        "total_expenses": total_expenses,
        "net_balance": net_balance,
    }