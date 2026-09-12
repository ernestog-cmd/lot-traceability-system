from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.schemas import ProductFamilyCreate, ProductFamilyResponse
from app.models.db_models import UserDB
from app.services import product_family_service
from app.auth.dependencies import require_role

router = APIRouter(prefix="/product-families", tags=["Product Families"])


@router.get("/", response_model=list[ProductFamilyResponse])
def get_families(db: Session = Depends(get_db)):
    """Return all product families."""
    return product_family_service.get_all_families(db)


@router.get("/active", response_model=list[ProductFamilyResponse])
def get_active_families(db: Session = Depends(get_db)):
    """Return only active product families."""
    return product_family_service.get_active_families(db)


@router.post("/", response_model=ProductFamilyResponse, status_code=201)
def create_family(
    data: ProductFamilyCreate,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """Propose a new product family. Engineer only. Requires QE approval."""
    return product_family_service.create_family(db, data, current_user.username)


@router.patch("/{name}/approve", response_model=ProductFamilyResponse)
def approve_family(
    name: str,
    db: Session = Depends(get_db),
    current_user: UserDB = Depends(require_role("engineer"))
):
    """Approve a pending product family. QE engineer only."""
    return product_family_service.approve_family(db, name, current_user.username)