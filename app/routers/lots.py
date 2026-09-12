from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.models.schemas import LotCreate, LotResponse, LotStatus
from app.models.db_models import UserDB
from app.services import lot_service
from app.auth.dependencies import require_role

router = APIRouter(prefix="/lots", tags=["Lots"])


class AuditRequest(BaseModel):
    username: str
    password: str


class DispositionRequest(BaseModel):
    decision: LotStatus
    ncr_number: str | None = None


class SignRequest(BaseModel):
    username: str
    password: str


@router.get("/", response_model=list[LotResponse])
def get_lots(db: Session = Depends(get_db)):
    """Return all lots."""
    return lot_service.get_all_lots(db)


@router.get("/{batch_id}", response_model=LotResponse)
def get_lot(batch_id: int, db: Session = Depends(get_db)):
    """Return a single lot by its internal batch_id."""
    return lot_service.get_lot(batch_id, db)


@router.post("/", response_model=LotResponse, status_code=201)
def create_lot(
    data: LotCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("manufacturing", "engineer"))
):
    """Register a new lot. Manufacturing or engineer only."""
    return lot_service.create_lot(data, db, current_user.username)


@router.patch("/{batch_id}/audit", response_model=LotResponse)
def audit_lot(batch_id: int, body: AuditRequest, db: Session = Depends(get_db)):
    """Auditor signs in with credentials to take a lot into audit process."""
    return lot_service.audit_lot(batch_id, body.username, body.password, db)


@router.patch("/{batch_id}/disposition", response_model=LotResponse)
def dispose_lot(
    batch_id: int,
    body: DispositionRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("auditor"))
):
    """Release or hold a lot. Auditor only. Hold requires NCR number."""
    return lot_service.dispose_lot(batch_id, body.decision, body.ncr_number, db)


@router.patch("/{batch_id}/return-from-hold", response_model=LotResponse)
def return_from_hold(batch_id: int, body: SignRequest, db: Session = Depends(get_db)):
    """Sign a lot return from hold. Requires both engineer and manufacturing signatures."""
    return lot_service.sign_return_from_hold(batch_id, body.username, body.password, db)