from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import UserCreate, UserResponse, UserRoleUpdate
from app.services import user_service
from app.auth.dependencies import require_role

router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    List all users in the system.

    **Admin only.** Returns every user regardless of active status,
    including their current role.
    """
    return user_service.get_all_users(db)


@router.post("/", response_model=UserResponse, status_code=201)
def create_user(
    data: UserCreate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Create a new user account.

    **Admin only.** The `role` must be one of: `admin`, `engineer`,
    `manufacturing`, `auditor`. New users are active by default.
    Fails with 409 if the username is already taken.
    """
    return user_service.create_user(data, db)


@router.patch("/{username}/toggle-active", response_model=UserResponse)
def toggle_active(
    username: str,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Activate or deactivate a user account.

    **Admin only.** Flips the user's active status. Inactive users
    cannot log in, even with correct credentials.
    """
    return user_service.toggle_active(username, db)


@router.patch("/{username}/role", response_model=UserResponse)
def update_role(
    username: str,
    data: UserRoleUpdate,
    db: Session = Depends(get_db),
    _=Depends(require_role("admin"))
):
    """
    Change a user's role.

    **Admin only.** Used when an employee changes position — e.g. a
    Manufacturing lead promoted to Quality Engineer.
    """
    return user_service.update_role(username, data.role, db)