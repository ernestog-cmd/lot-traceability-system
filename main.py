from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import Lot
from database import engine, Base, get_db
import db_models

Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Lot Traceability System is running"}

@app.get("/lots")
def get_lots(db: Session = Depends(get_db)):
    return db.query(db_models.LotDB).all()

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
    return new_lot