from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import Optional
from datetime import date
from app.database import SessionLocal
from app.models import Transaction
from app.schemas import TransactionCreate, TransactionOut, TransactionUpdate
from app.dependencies import get_current_user, require_roles
from app.utils import log_action

router = APIRouter(prefix="/transactions", tags=["Transactions"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=TransactionOut)
def create_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    new_transaction = Transaction(**transaction.dict(), owner_id=current_user.id)
    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    log_action(db, current_user.id, "CREATE", "Transaction", new_transaction.id)

    return new_transaction


@router.get("/", response_model=list[TransactionOut])
def get_transactions(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["viewer", "analyst", "admin"])),
    tx_type: Optional[str] = None,
    category: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = Query(10, le=100)
):
    query = db.query(Transaction).filter(Transaction.is_deleted == False)

    if current_user.role != "admin":
        query = query.filter(Transaction.owner_id == current_user.id)

    if tx_type:
        query = query.filter(Transaction.type == tx_type)

    if category:
        query = query.filter(Transaction.category == category)

    if start_date:
        query = query.filter(Transaction.date >= start_date)

    if end_date:
        query = query.filter(Transaction.date <= end_date)

    if search:
        query = query.filter(
            or_(
                Transaction.notes.ilike(f"%{search}%"),
                Transaction.category.ilike(f"%{search}%"),
                Transaction.merchant.ilike(f"%{search}%")
            )
        )

    return query.offset(skip).limit(limit).all()


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction_by_id(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["viewer", "analyst", "admin"]))
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if current_user.role != "admin" and transaction.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    return transaction


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: int,
    updated_data: TransactionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    for key, value in updated_data.dict(exclude_unset=True).items():
        setattr(transaction, key, value)

    db.commit()
    db.refresh(transaction)

    log_action(db, current_user.id, "UPDATE", "Transaction", transaction.id)

    return transaction


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["admin"]))
):
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.is_deleted == False
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.is_deleted = True
    db.commit()

    log_action(db, current_user.id, "DELETE", "Transaction", transaction.id)

    return {"message": "Transaction soft deleted successfully"}