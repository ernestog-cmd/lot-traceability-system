from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import PartNumber
from app.models.schemas import PartNumberCreate, PartNumberResponse
from app.services import part_number_service

router = APIRouter(prefix="/part-numbers", tags=["Part Numbers"])

@router.get("/", response_model=list[PartNumberResponse])
def get_part_numbers(db: Session = Depends(get_db)):
    """Return all registered part numbers, ordered by code"""
    return part_number_service.get_all_part_numbers(db)

@router.post("/", response_model=PartNumberResponse, status_code=201)
def create_part_number(data: PartNumberCreate, db: Session = Depends(get_db)):
    """Register a new part number. Code must be unique"""
    existing = db.query(__import__('app.models.db_models', fromlist=['PartNumber']).PartNumber).filter_by(code=data.code).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Part number '{data.code}' already exists")
    return part_number_service.create_part_number(db, data)
