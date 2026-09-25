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
    """
    List all part numbers, regardless of approval status.

    Includes part numbers still `pending_qe_approval` alongside
    `active` ones.
    """
    return part_number_service.get_all_part_numbers(db)


@router.get("/active", response_model=list[PartNumberResponse])
def get_active_part_numbers(db: Session = Depends(get_db)):
    """
    List only approved (active) part numbers.

    This is the endpoint the lot creation form uses to populate its
    part number dropdown — a lot can only reference an active part
    number.
    """
    return part_number_service.get_all_active_part_numbers(db)


@router.post("/", response_model=PartNumberResponse, status_code=201)
def create_part_number(
    data: PartNumberCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """
    Propose a new part number.

    **Engineer only.** The `family_name` must reference an existing,
    active product family. The part number is created with status
    `pending_qe_approval` and cannot be used to create lots until a
    Quality Engineer approves it.
    """
    return part_number_service.create_part_number(db, data, current_user.username)


@router.patch("/{code}/approve", response_model=PartNumberResponse)
def approve_part_number(
    code: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """
    Approve a pending part number.

    **Engineer (QE) only.** Moves the part number's status from
    `pending_qe_approval` to `active`. Fails with 409 if it is not
    currently pending.
    """
    return part_number_service.approve_part_number(db, code, current_user.username)