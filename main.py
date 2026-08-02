from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Lot, Auditor
from database import engine, Base, get_db
from datetime import datetime
import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI()

def lot_db_to_response(lot_db: db_models.LotDB) -> Lot:
    auditor = None
    if lot_db.audited_by_system_user:
        auditor = Auditor(
            first_name = lot_db.audited_by_first_name,
            last_name = lot_db.audited_by_last_name,
            system_user = lot_db.audited_by_system_user,
        )
    return Lot(
        id=lot_db.id,
        part_number=lot_db.part_number,
        description=lot_db.description,
        product_family=lot_db.product_family,
        units=lot_db.units,
        manufacturing_date=lot_db.manufacturing_date,
        status=lot_db.status,
        audited_by= auditor,
        audited_at=lot_db.audited_at,
    )

@app.get("/")
def read_root():
    return {"message": "Lot Traceability System is running"}

@app.get("/lots")
def get_lots(db: Session = Depends(get_db)):
    lots_db = db.query(db_models.LotDB).all()
    return [lot_db_to_response(lot) for lot in lots_db]


@app.post("/lots") 
def create_lot(lot: Lot, db: Session = Depends(get_db)):
    new_lot = db_models.LotDB(
        id=lot.id,
        part_number=lot.part_number,
        description=lot.description,
        product_family=lot.product_family,
        units=lot.units,
        manufacturing_date=lot.manufacturing_date,
        status=lot.status.value,
        audited_by_first_name=lot.audited_by.first_name if lot.audited_by else None,
        audited_by_last_name=lot.audited_by.last_name if lot.audited_by else None,
        audited_by_system_user=lot.audited_by.system_user if lot.audited_by else None,
        audited_at= lot.audited_at,
    )   
    db.add(new_lot)
    db.commit()
    db.refresh(new_lot)
    return lot_db_to_response(new_lot)


@app.get("/lots/{lot_id}")
def get_lot(lot_id: str, db: Session = Depends(get_db)):
    lot = db.query(db_models.LotDB).filter(db_models.LotDB.id == lot_id).first()
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} not found")
    return lot_db_to_response(lot)

@app.patch("/lots/{lot_id}/audit")
def audit_lot(lot_id: str, auditor: Auditor, db: Session = Depends(get_db)):
    lot = db.query(db_models.LotDB).filter(db_models.LotDB.id == lot_id).first()
    if lot is None:
        raise HTTPException(status_code=404, detail=f"Lot {lot_id} not found")

    if lot.status != "ready_for_audit":
        raise HTTPException(status_code=409, detail=f"Lot {lot_id} cannot be audited: current status is '{lot.status}'")

    lot.status = "in_audit_process"
    lot.audited_by_first_name = auditor.first_name
    lot.audited_by_last_name = auditor.last_name
    lot.audited_by_system_user = auditor.system_user
    lot.audited_at = datetime.now()

    db.commit()
    db.refresh(lot)
    return lot_db_to_response(lot)

