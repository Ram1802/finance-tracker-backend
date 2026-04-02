from sqlalchemy.orm import Session
from sqlalchemy import func, extract
from app.models import Transaction


def get_summary_data(db: Session, user_id: int = None, is_admin: bool = False):
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    if not is_admin and user_id:
        query = query.filter(Transaction.owner_id == user_id)

    income = query.filter(Transaction.type == "income").with_entities(func.sum(Transaction.amount)).scalar() or 0
    expense = query.filter(Transaction.type == "expense").with_entities(func.sum(Transaction.amount)).scalar() or 0

    return {
        "total_income": income,
        "total_expenses": expense,
        "current_balance": income - expense
    }


def get_category_breakdown_data(db: Session, user_id: int = None, is_admin: bool = False):
    query = db.query(
        Transaction.category,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.is_deleted == False)

    if not is_admin and user_id:
        query = query.filter(Transaction.owner_id == user_id)

    result = query.group_by(Transaction.category).all()

    return [{"category": row[0], "total": row[1]} for row in result]


def get_monthly_breakdown_data(db: Session, user_id: int = None, is_admin: bool = False):
    query = db.query(
        extract("month", Transaction.date).label("month"),
        Transaction.type,
        func.sum(Transaction.amount).label("total")
    ).filter(Transaction.is_deleted == False)

    if not is_admin and user_id:
        query = query.filter(Transaction.owner_id == user_id)

    data = query.group_by(extract("month", Transaction.date), Transaction.type).all()

    result = {}
    for month, tx_type, total in data:
        month_key = f"Month-{int(month)}"
        if month_key not in result:
            result[month_key] = {"month": month_key, "total_income": 0, "total_expense": 0}

        if tx_type == "income":
            result[month_key]["total_income"] = total
        elif tx_type == "expense":
            result[month_key]["total_expense"] = total

    return list(result.values())