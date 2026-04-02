from sqlalchemy.orm import Session
from app.models import User
from app.auth import hash_password


def seed_admin(db: Session):
    admin_user = db.query(User).filter(User.username == "admin").first()
    if not admin_user:
        admin = User(
            username="admin",
            password=hash_password("admin123"),
            role="admin"
        )
        db.add(admin)
        db.commit()