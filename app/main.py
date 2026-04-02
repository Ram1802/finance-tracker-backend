from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine, SessionLocal
from app.routes.users import router as users_router
from app.routes.transactions import router as transactions_router
from app.routes.analytics import router as analytics_router
from app.routes.budgets import router as budgets_router
from app.routes.goals import router as goals_router
from app.routes.reports import router as reports_router
from app.seed import seed_admin

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Finance Tracker Backend",
    description="Industry-level finance tracking backend with authentication, analytics, budgets, goals, reports, and role-based access.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(transactions_router)
app.include_router(analytics_router)
app.include_router(budgets_router)
app.include_router(goals_router)
app.include_router(reports_router)


@app.get("/")
def root():
    return {"message": "Finance Tracker Backend API is running successfully"}


db = SessionLocal()
seed_admin(db)
db.close()