from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import UserDB
from app.auth.security import verify_password, create_access_token
from app.auth.dependencies import get_current_user
from app.core.logging_config import get_logger
from pydantic import BaseModel

router = APIRouter(prefix="/auth", tags=["Auth"])
logger = get_logger(__name__)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    role: str
    is_active: str

    model_config = {"from_attributes": True}


@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate a user and return a JWT access token."""
    user = db.query(UserDB).filter_by(username=form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        logger.warning(f"Failed login attempt for username '{form_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if user.is_active != "true":
        logger.warning(f"Login attempt for inactive user '{form_data.username}'")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    token = create_access_token({"sub": user.username, "role": user.role})
    logger.info(f"User '{user.username}' logged in successfully (role={user.role})")
    return {"access_token": token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserDB = Depends(get_current_user)):
    """Return the currently authenticated user's profile."""
    return current_user