from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Goal
from app.schemas import GoalCreate, GoalOut, GoalUpdate
from app.dependencies import get_current_user

router = APIRouter(prefix="/goals", tags=["Goals"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=GoalOut)
def create_goal(
    goal: GoalCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    new_goal = Goal(**goal.model_dump(), owner_id=current_user.id)
    db.add(new_goal)
    db.commit()
    db.refresh(new_goal)
    return new_goal


@router.get("/", response_model=list[GoalOut])
def get_goals(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return db.query(Goal).filter(Goal.owner_id == current_user.id).all()


@router.put("/{goal_id}", response_model=GoalOut)
def update_goal_progress(
    goal_id: int,
    goal_data: GoalUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    goal = db.query(Goal).filter(
        Goal.id == goal_id,
        Goal.owner_id == current_user.id
    ).first()

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    if goal_data.saved_amount is not None:
        goal.saved_amount = goal_data.saved_amount

    db.commit()
    db.refresh(goal)
    return goal


@router.get("/progress")
def get_goal_progress(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    goals = db.query(Goal).filter(Goal.owner_id == current_user.id).all()

    result = []
    for goal in goals:
        progress = (goal.saved_amount / goal.target_amount) * 100 if goal.target_amount > 0 else 0
        result.append({
            "goal_name": goal.name,
            "target_amount": goal.target_amount,
            "saved_amount": goal.saved_amount,
            "progress_percentage": round(progress, 2)
        })

    return result