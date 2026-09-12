from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import UserCreate, UserResponse
from app.services import user_service
from app.auth.dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db), _: None = Depends(require_role("admin"))):
    """List all users. admin only"""
    return user_service.get_all_users(db)

@router.post("/", response_model=UserResponse, status_code=201)
def create_user(data: UserCreate, db: Session = Depends(get_db), _: None = Depends(require_role("admin"))):
    """Create a new user. Admin only"""
    return user_service.create_user(data, db)
