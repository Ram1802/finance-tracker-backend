from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Budget, Transaction
from app.schemas import BudgetCreate, BudgetOut
from app.dependencies import get_current_user

router = APIRouter(prefix="/budgets", tags=["Budgets"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=BudgetOut)
def create_budget(
    budget: BudgetCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_budget = Budget(**budget.dict(), owner_id=current_user.id)
    db.add(new_budget)
    db.commit()
    db.refresh(new_budget)
    return new_budget


@router.get("/", response_model=list[BudgetOut])
def get_budgets(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Budget).filter(Budget.owner_id == current_user.id).all()


@router.get("/status")
def get_budget_status(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    budgets = db.query(Budget).filter(Budget.owner_id == current_user.id).all()

    result = []
    for budget in budgets:
        spent = db.query(Transaction).filter(
            Transaction.owner_id == current_user.id,
            Transaction.category == budget.category,
            Transaction.type == "expense",
            Transaction.is_deleted == False
        ).with_entities(Transaction.amount).all()

        total_spent = sum([item[0] for item in spent]) if spent else 0

        result.append({
            "category": budget.category,
            "budget": budget.amount,
            "spent": total_spent,
            "remaining": budget.amount - total_spent,
            "status": "overspent" if total_spent > budget.amount else "within budget"
        })

    return result