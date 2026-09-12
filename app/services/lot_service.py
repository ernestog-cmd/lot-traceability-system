from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import LotDB, PartNumber, UserDB
from app.models.schemas import LotCreate, LotStatus
from app.auth.security import verify_password


def _to_response(lot: LotDB, db: Session) -> dict:
    part_number = db.query(PartNumber).filter_by(code=lot.part_number_code).first()
    audited_by = None
    if lot.audited_by_system_user:
        audited_by = {
            "first_name": lot.audited_by_first_name,
            "last_name": lot.audited_by_last_name,
            "system_user": lot.audited_by_system_user,
        }
    return {
        "batch_id": lot.batch_id,
        "lot_id": lot.lot_id,
        "part_number_code": lot.part_number_code,
        "part_number_description": part_number.description if part_number else None,
        "product_family": lot.product_family,
        "units": lot.units,
        "manufacturing_date": lot.manufacturing_date,
        "status": lot.status,
        "audited_by": audited_by,
        "audited_at": lot.audited_at,
        "ncr_number": lot.ncr_number,
        "me_approved_by": lot.me_approved_by,
        "qe_approved_by": lot.qe_approved_by,
    }


def get_all_lots(db: Session) -> list[dict]:
    lots = db.query(LotDB).all()
    return [_to_response(lot, db) for lot in lots]


def get_lot(batch_id: int, db: Session) -> dict:
    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    return _to_response(lot, db)


def create_lot(data: LotCreate, db: Session, created_by: str) -> dict:
    part_number = db.query(PartNumber).filter_by(code=data.part_number_code, status="active").first()
    if not part_number:
        raise HTTPException(status_code=404, detail=f"Part number '{data.part_number_code}' not found or not active")

    existing = db.query(LotDB).filter_by(lot_id=data.lot_id, part_number_code=data.part_number_code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Lot '{data.lot_id}' with part number '{data.part_number_code}' already exists")

    lot = LotDB(
        lot_id=data.lot_id,
        part_number_code=data.part_number_code,
        product_family=part_number.family_name,
        units=data.units,
        manufacturing_date=data.manufacturing_date,
        status=LotStatus.READY_FOR_AUDIT.value,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)


def audit_lot(batch_id: int, username: str, password: str, db: Session) -> dict:
    user = db.query(UserDB).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.role != "auditor":
        raise HTTPException(status_code=403, detail="Only auditors can audit lots")

    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    if lot.status != LotStatus.READY_FOR_AUDIT.value:
        raise HTTPException(status_code=409, detail=f"Lot cannot be audited: current status is '{lot.status}'")

    lot.status = LotStatus.IN_AUDIT_PROCESS.value
    lot.audited_by_first_name = user.first_name
    lot.audited_by_last_name = user.last_name
    lot.audited_by_system_user = user.username
    lot.audited_at = datetime.now()
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)


def dispose_lot(batch_id: int, decision: LotStatus, ncr_number: str | None, db: Session) -> dict:
    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    if lot.status != LotStatus.IN_AUDIT_PROCESS.value:
        raise HTTPException(status_code=409, detail=f"Lot cannot be dispositioned: current status is '{lot.status}'")
    if decision not in (LotStatus.RELEASED, LotStatus.HOLD):
        raise HTTPException(status_code=422, detail="Disposition must be 'released' or 'hold'")
    if decision == LotStatus.HOLD and not ncr_number:
        raise HTTPException(status_code=422, detail="NCR number is required when placing a lot on hold")

    lot.status = decision.value
    if decision == LotStatus.HOLD:
        lot.ncr_number = ncr_number
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)


def sign_return_from_hold(batch_id: int, username: str, password: str, db: Session) -> dict:
    user = db.query(UserDB).filter_by(username=username).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.role not in ("engineer", "manufacturing"):
        raise HTTPException(status_code=403, detail="Only engineers and manufacturing leads can sign lot returns")

    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")

    valid_statuses = (
        LotStatus.HOLD.value,
        LotStatus.WAITING_ME_APPROVAL.value,
        LotStatus.WAITING_QE_APPROVAL.value,
    )
    if lot.status not in valid_statuses:
        raise HTTPException(status_code=409, detail=f"Lot is not in a returnable status: '{lot.status}'")

    if user.role == "engineer":
        if lot.qe_approved_by:
            raise HTTPException(status_code=409, detail="QE has already signed this lot")
        lot.qe_approved_by = user.username
        if lot.me_approved_by:
            lot.status = LotStatus.READY_FOR_AUDIT.value
        else:
            lot.status = LotStatus.WAITING_ME_APPROVAL.value

    elif user.role == "manufacturing":
        if lot.me_approved_by:
            raise HTTPException(status_code=409, detail="Manufacturing has already signed this lot")
        lot.me_approved_by = user.username
        if lot.qe_approved_by:
            lot.status = LotStatus.READY_FOR_AUDIT.value
        else:
            lot.status = LotStatus.WAITING_QE_APPROVAL.value

    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)