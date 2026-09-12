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
        raise HTTPException(status_code=409, detail=f"Username '{data.username}' already exists.")
    user = UserDB(
        username=data.username,
        hashed_password=hash_password(data.password),
        first_name=data.first_name,
        last_name=data.last_name,
        role=data.role
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

def get_all_users(db: Session) -> list[UserDB]:
    return db.query(UserDB).all()
