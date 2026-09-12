from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import PartNumberCreate, PartNumberResponse
from app.models.db_models import UserDB
from app.services import part_number_service
from app.auth.dependencies import require_role

router = APIRouter(prefix="/part-numbers", tags=["Part Numbers"])


@router.get("/", response_model=list[PartNumberResponse])
def get_part_numbers(db: Session = Depends(get_db)):
    """Return all part numbers."""
    return part_number_service.get_all_part_numbers(db)


@router.get("/active", response_model=list[PartNumberResponse])
def get_active_part_numbers(db: Session = Depends(get_db)):
    """Return only active part numbers (for lot creation dropdown)."""
    return part_number_service.get_all_active_part_numbers(db)


@router.post("/", response_model=PartNumberResponse, status_code=201)
def create_part_number(
    data: PartNumberCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """Propose a new part number. Engineer only. Requires QE approval."""
    return part_number_service.create_part_number(db, data, current_user.username)


@router.patch("/{code}/approve", response_model=PartNumberResponse)
def approve_part_number(
    code: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """Approve a pending part number. QE engineer only."""
    return part_number_service.approve_part_number(db, code, current_user.username)