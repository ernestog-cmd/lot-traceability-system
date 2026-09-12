from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import UserDB
from app.models.schemas import UserCreate
from app.auth.security import hash_password

VALID_ROLES = {"admin", "manufacturing", "engineer", "auditor"}


def create_user(data: UserCreate, db: Session) -> UserDB:
    if data.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role '{data.role}'. Valid roles: {VALID_ROLES}")

    existing = db.query(UserDB).filter_by(username=data.username).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Username '{data.username}' already exists")

    user = UserDB(
        username=data.username,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role,
        is_active="true",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_all_users(db: Session) -> list[UserDB]:
    return db.query(UserDB).all()


def toggle_active(username: str, db: Session) -> UserDB:
    user = db.query(UserDB).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    user.is_active = "false" if user.is_active == "true" else "true"
    db.commit()
    db.refresh(user)
    return user


def update_role(username: str, role: str, db: Session) -> UserDB:
    if role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role '{role}'")
    user = db.query(UserDB).filter_by(username=username).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User '{username}' not found")
    user.role = role
    db.commit()
    db.refresh(user)
    return user