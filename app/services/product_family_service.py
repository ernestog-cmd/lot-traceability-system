from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models.db_models import ProductFamily
from app.models.schemas import ProductFamilyCreate


def get_all_families(db: Session) -> list[ProductFamily]:
    return db.query(ProductFamily).order_by(ProductFamily.name).all()


def get_active_families(db: Session) -> list[ProductFamily]:
    return db.query(ProductFamily).filter_by(status="active").order_by(ProductFamily.name).all()


def create_family(db: Session, data: ProductFamilyCreate, proposed_by: str) -> ProductFamily:
    existing = db.query(ProductFamily).filter_by(name=data.name).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Product family '{data.name}' already exists")

    family = ProductFamily(
        name=data.name,
        status="pending_qe_approval",
        proposed_by=proposed_by,
    )
    db.add(family)
    db.commit()
    db.refresh(family)
    return family


def approve_family(db: Session, name: str, approved_by: str) -> ProductFamily:
    family = db.query(ProductFamily).filter_by(name=name).first()
    if not family:
        raise HTTPException(status_code=404, detail=f"Product family '{name}' not found")
    if family.status != "pending_qe_approval":
        raise HTTPException(status_code=409, detail=f"Product family '{name}' is not pending approval")

    family.status = "active"
    family.approved_by = approved_by
    db.commit()
    db.refresh(family)
    return family