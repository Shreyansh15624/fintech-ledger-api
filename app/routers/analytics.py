from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models
from app.database import get_db
from app.security.dependencies import RoleChecker

router = APIRouter()

# SUMMARY ENDPOINT (Locked to Admin & Analyst Roles)
@router.get("/summary")
def get_financial_summary(
    db: Session = Depends(get_db),
    # Limit the privileges to 'Analyst' & 'Admin' roles
    current_employee: models.Employee = Depends(RoleChecker({"Analyst", "Admin"}))
):

        # A) BASE TOTALS
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

        # B) EXPENSE METRICS (Velocity & Average Values)
    # 1. No. of entries for `record_type` (Count)
    expense_count = db.query(func.count(models.Record.id)).filter(
        models.Record.record_type == "expense"
    ).scalar() or 0

    # 2. Average Values (`expense`)
    avg_value = db.query(func.avg(models.Record.amount)).filter(
        models.Record.record_type == "expense"
    ).scalar() or 0.0
    
        # C) EXPENSE BREAKDOWN (Grouping by `category`)
    category_data = db.query(
        models.Record.category,
        func.sum(models.Record.amount)
    ).filter(
        models.Record.record_type == "expense"
    ).group_by(
        models.Record.category
    ).all()

    expense_breakdown = {cat: amt for cat, amt in category_data}
    
        # D) TOP `n` HIGHEST EXPENSES
    # Requesting the appropriate Sorted Data from the DB 
    total_expense_data = db.query(
        models.Record.category,
        models.Record.amount,
    ).filter(
        models.Record.record_type == "expense"
    ).order_by(
        models.Record.amount.desc()
    ).limit(3).all()

    # Formatting the Top Expenses for our Schema
    top_expenses = [
        {"category": cat, "amount": amt}
        for cat, amt in total_expense_data
    ]

    # The Data Transfer Object (DTO) Assembly
    return {
        "totals": {
            "total_income": total_income,
            "total_expenses": total_expenses,
            "net_balance": net_balance,
        },
        "metrics": {
            "total_transaction_count": expense_count,
            "average_expense_value": round(avg_value, 2)
        },
        "expense_breakdown": expense_breakdown,
        "top_expense": top_expenses,
    }