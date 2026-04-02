from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.dependencies import require_roles
from app.services.analytics_service import (
    get_summary_data,
    get_category_breakdown_data,
    get_monthly_breakdown_data
)

router = APIRouter(prefix="/analytics", tags=["Analytics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/summary")
def get_summary(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["viewer", "analyst", "admin"]))
):
    return get_summary_data(
        db,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )


@router.get("/category-breakdown")
def category_breakdown(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["analyst", "admin"]))
):
    return get_category_breakdown_data(
        db,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )


@router.get("/monthly-breakdown")
def monthly_breakdown(
    db: Session = Depends(get_db),
    current_user=Depends(require_roles(["analyst", "admin"]))
):
    return get_monthly_breakdown_data(
        db,
        user_id=current_user.id,
        is_admin=current_user.role == "admin"
    )