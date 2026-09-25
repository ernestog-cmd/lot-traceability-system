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
    """
    List all lots, across every lifecycle status.

    This is the single source of data the frontend uses for the
    dashboard, Active Lots, History, Audits, and Reports views —
    each view filters this list client-side by status.
    """
    return lot_service.get_all_lots(db)


@router.get("/{batch_id}", response_model=LotResponse)
def get_lot(batch_id: int, db: Session = Depends(get_db)):
    """
    Get a single lot by its internal `batch_id`.

    Note this is not the same as `lot_id`: a `lot_id` can repeat
    across different part numbers, so `batch_id` is the unique
    identifier used in URLs.
    """
    return lot_service.get_lot(batch_id, db)


@router.post("/", response_model=LotResponse, status_code=201)
def create_lot(
    data: LotCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("manufacturing", "engineer"))
):
    """
    Register a new lot in `ready_for_audit` status.

    **Manufacturing or Engineer only.** The `part_number_code` must
    reference an active part number; its `product_family` is copied
    onto the lot automatically. Fails with 409 if the same
    `lot_id` + `part_number_code` combination already exists.
    """
    return lot_service.create_lot(data, db, current_user.username)


@router.patch("/{batch_id}/audit", response_model=LotResponse)
def audit_lot(batch_id: int, body: AuditRequest, db: Session = Depends(get_db)):
    """
    Take a lot into the audit process.

    The auditor authenticates with their own username and password
    in the request body (not a bearer token) — this is a deliberate
    signature step, similar to signing a paper traveler. On success
    the auditor's name is recorded on the lot automatically. The lot
    must currently be in `ready_for_audit` status.
    """
    return lot_service.audit_lot(batch_id, body.username, body.password, db)


@router.patch("/{batch_id}/disposition", response_model=LotResponse)
def dispose_lot(
    batch_id: int,
    body: DispositionRequest,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("auditor"))
):
    """
    Release or hold a lot after audit.

    **Auditor only.** The lot must be in `in_audit_process` status.
    A `decision` of `hold` requires an `ncr_number` in the request
    body — the API rejects a hold disposition without one.
    """
    return lot_service.dispose_lot(batch_id, body.decision, body.ncr_number, db)


@router.patch("/{batch_id}/return-from-hold", response_model=LotResponse)
def return_from_hold(batch_id: int, body: SignRequest, db: Session = Depends(get_db)):
    """
    Sign off on returning a held lot to `ready_for_audit`.

    Requires two independent signatures — one Quality Engineer and
    one Manufacturing lead — authenticated by their own credentials
    in the request body, same pattern as the audit endpoint. The
    first signature moves the lot to `waiting_me_approval` or
    `waiting_qe_approval` depending on who signed first; the second
    matching signature completes the return. The NCR number and both
    signatures are preserved on the lot as history even after it
    returns to `ready_for_audit`.
    """
    return lot_service.sign_return_from_hold(batch_id, body.username, body.password, db)