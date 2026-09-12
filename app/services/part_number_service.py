from sqlalchemy.orm import Session
from app.models.db_models import PartNumber
from app.models.schemas import PartNumberCreate

def get_all_part_numbers(db: Session) -> list[PartNumber]:
    return db.query(PartNumber).order_by(PartNumber.code).all()

def create_part_number(db: Session, data: PartNumberCreate) -> PartNumber:
    part_number = PartNumber(code=data.code, description=data.description)
    db.add(part_number)
    db.commit()
    db.refresh(part_number)
    return part_number

