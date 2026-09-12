from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import PartNumber, ProductFamily
from app.models.schemas import PartNumberCreate


def get_all_active_part_numbers(db: Session) -> list[PartNumber]:
    return db.query(PartNumber).filter_by(status="active").order_by(PartNumber.code).all()


def get_all_part_numbers(db: Session) -> list[PartNumber]:
    return db.query(PartNumber).order_by(PartNumber.code).all()


def create_part_number(db: Session, data: PartNumberCreate, proposed_by: str) -> PartNumber:
    print(f"DEBUG: looking for family '{data.family_name}' with status active")
    family = db.query(ProductFamily).filter_by(name=data.family_name, status="active").first()
    print(f"DEBUG: family found: {family}")

    if not family:
        raise HTTPException(status_code=404, detail=f"Product family '{data.family_name}' not found or not active")

    print(f"DEBUG: looking for existing PN '{data.code}'")
    existing = db.query(PartNumber).filter_by(code=data.code).first()
    print(f"DEBUG: existing: {existing}")

    if existing:
        raise HTTPException(status_code=409, detail=f"Part number '{data.code}' already exists")

    print(f"DEBUG: creating PN")
    part_number = PartNumber(
        code=data.code,
        description=data.description,
        family_name=data.family_name,
        status="pending_qe_approval",
        proposed_by=proposed_by,
    )
    db.add(part_number)
    db.commit()
    db.refresh(part_number)
    print(f"DEBUG: PN created successfully")
    return part_number


def approve_part_number(db: Session, code: str, approved_by: str) -> PartNumber:
    pn = db.query(PartNumber).filter_by(code=code).first()
    if not pn:
        raise HTTPException(status_code=404, detail=f"Part number '{code}' not found")
    if pn.status != "pending_qe_approval":
        raise HTTPException(status_code=409, detail=f"Part number '{code}' is not pending approval")

    pn.status = "active"
    pn.approved_by = approved_by
    db.commit()
    db.refresh(pn)
    return pn