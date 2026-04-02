from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Transaction
from app.dependencies import get_current_user
import pandas as pd
import os

router = APIRouter(prefix="/reports", tags=["Reports"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/export/csv")
def export_transactions_csv(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    transactions = db.query(Transaction).filter(
        Transaction.owner_id == current_user.id,
        Transaction.is_deleted == False
    ).all()

    data = []
    for tx in transactions:
        data.append({
            "id": tx.id,
            "amount": tx.amount,
            "type": tx.type,
            "category": tx.category,
            "date": tx.date,
            "notes": tx.notes,
            "payment_method": tx.payment_method,
            "currency": tx.currency,
            "merchant": tx.merchant,
            "status": tx.status
        })

    if not os.path.exists("exports"):
        os.makedirs("exports")

    file_path = f"exports/user_{current_user.id}_transactions.csv"
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)

    return FileResponse(file_path, media_type="text/csv", filename="transactions.csv")