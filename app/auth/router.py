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
    """
    Authenticate with username and password, receive a JWT access token.

    Uses the standard OAuth2 password flow (`application/x-www-form-urlencoded`
    body with `username` and `password` fields — this is why Swagger's
    "Try it out" shows a form here instead of a JSON body). The
    returned `access_token` must be sent as `Authorization: Bearer <token>`
    on protected endpoints. Inactive users are rejected with 403 even
    with correct credentials.
    """
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
    """
    Return the profile of the currently authenticated user.

    Reads the bearer token from the `Authorization` header and
    resolves it back to the user record. Used by the frontend right
    after login to know which role's UI to render.
    """
    return current_user