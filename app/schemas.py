from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date


# ---------------- USERS ----------------
class UserCreate(BaseModel):
    username: str
    password: str
    role: str = "viewer"


class UserLogin(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str
    role: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


# ---------------- TRANSACTIONS ----------------
class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str
    category: str
    date: date
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = "INR"
    merchant: Optional[str] = None
    status: Optional[str] = "completed"
    is_recurring: Optional[bool] = False


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    type: Optional[str] = None
    category: Optional[str] = None
    date: Optional[date] = None
    notes: Optional[str] = None
    payment_method: Optional[str] = None
    currency: Optional[str] = None
    merchant: Optional[str] = None
    status: Optional[str] = None
    is_recurring: Optional[bool] = None


class TransactionOut(BaseModel):
    id: int
    amount: float
    type: str
    category: str
    date: date
    notes: Optional[str]
    payment_method: Optional[str]
    currency: Optional[str]
    merchant: Optional[str]
    status: Optional[str]
    is_recurring: Optional[bool]

    class Config:
        from_attributes = True


# ---------------- BUDGETS ----------------
class BudgetCreate(BaseModel):
    category: str
    amount: float = Field(..., gt=0)
    month: str


class BudgetOut(BaseModel):
    id: int
    category: str
    amount: float
    month: str

    class Config:
        from_attributes = True


# ---------------- GOALS ----------------
class GoalCreate(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    saved_amount: Optional[float] = 0
    target_date: Optional[date] = None


class GoalUpdate(BaseModel):
    saved_amount: Optional[float] = None


class GoalOut(BaseModel):
    id: int
    name: str
    target_amount: float
    saved_amount: float
    target_date: Optional[date]

    class Config:
        from_attributes = True