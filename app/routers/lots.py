from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import LotCreate, LotResponse, LotStatus, Auditor
from app.services import lot_service

router = APIRouter(prefix="/lots", tags=["Lots"])


@router.get("/", response_model=list[LotResponse])
def get_lots(db: Session = Depends(get_db)):
    """Return all lots."""
    return lot_service.get_all_lots(db)


@router.get("/{batch_id}", response_model=LotResponse)
def get_lot(batch_id: int, db: Session = Depends(get_db)):
    """Return a single lot by its internal batch_id."""
    return lot_service.get_lot(batch_id, db)


@router.post("/", response_model=LotResponse, status_code=201)
def create_lot(data: LotCreate, db: Session = Depends(get_db)):
    """Register a new lot. The part number must exist. lot_id + part_number_code must be unique."""
    return lot_service.create_lot(data, db)


@router.patch("/{batch_id}/audit", response_model=LotResponse)
def audit_lot(batch_id: int, auditor: Auditor, db: Session = Depends(get_db)):
    """Assign an auditor to a lot. Lot must be in ready_for_audit status."""
    return lot_service.audit_lot(batch_id, auditor, db)


@router.patch("/{batch_id}/disposition", response_model=LotResponse)
def dispose_lot(batch_id: int, decision: LotStatus, db: Session = Depends(get_db)):
    """Release or hold a lot. Lot must be in in_audit_process status."""
    return lot_service.dispose_lot(batch_id, decision, db)