from datetime import datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import LotDB, PartNumber
from app.models.schemas import LotCreate, LotStatus, Auditor

def _to_response(lot: LotDB, db: Session) -> dict:
    part_number = db.query(PartNumber).filter_by(code=lot.part_number_code).first()
    audited_by = None
    if lot.audited_by_system_user:
        audited_by = {
            "first_name" : lot.audited_by_first_name,
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
    }

def get_all_lots(db: Session) -> list[dict]:
    lots = db.query(LotDB).all()
    return [_to_response(lot, db) for lot in lots]


def get_lot(batch_id: int, db: Session) -> dict:
    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    return _to_response(lot, db)

def create_lot(data: LotCreate, db: Session) -> dict:
    part_number = db.query(PartNumber).filter_by(code=data.part_number_code).first()
    if not part_number:
        raise HTTPException(status_code=404, detail=f"Part number '{data.part_number_code}' not found")

    existing = db.query(LotDB).filter_by(lot_id=data.lot_id, part_number_code=data.part_number_code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Lot '{data.lot_id}' with part number '{data.part_number_code}' already exists")

    lot = LotDB(
        lot_id=data.lot_id,
        part_number_code=data.part_number_code,
        product_family=data.product_family,
        units=data.units,
        manufacturing_date=data.manufacturing_date,
        status=data.status.value,
    )
    db.add(lot)
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)

def audit_lot(batch_id: int, auditor: Auditor, db: Session) -> dict:
    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    if lot.status != LotStatus.READY_FOR_AUDIT:
        raise HTTPException(status_code=409, detail=f"Lot cannot be audited: current status is '{lot.status}'")

    lot.status = LotStatus.IN_AUDIT_PROCESS
    lot.audited_by_first_name = auditor.first_name
    lot.audited_by_last_name = auditor.last_name
    lot.audited_by_system_user = auditor.system_user
    lot.audited_at = datetime.now()
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)


def dispose_lot(batch_id: int, decision: LotStatus, db: Session) -> dict:
    lot = db.query(LotDB).filter_by(batch_id=batch_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail=f"Lot with batch_id {batch_id} not found")
    if lot.status != LotStatus.IN_AUDIT_PROCESS:
        raise HTTPException(status_code=409, detail=f"Lot cannot be dispositioned: current status is '{lot.status}'")
    if decision not in (LotStatus.RELEASED, LotStatus.HOLD):
        raise HTTPException(status_code=422, detail="Disposition must be 'released' or 'hold'")

    lot.status = decision.value
    db.commit()
    db.refresh(lot)
    return _to_response(lot, db)