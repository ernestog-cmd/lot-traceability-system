from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel


class LotStatus(str, Enum):
    READY_FOR_AUDIT = "ready_for_audit"
    IN_AUDIT_PROCESS = "in_audit_process"
    RELEASED = "released"
    HOLD = "hold"
    WAITING_ME_APPROVAL = "waiting_me_approval"
    WAITING_QE_APPROVAL = "waiting_qe_approval"


class ApprovalStatus(str, Enum):
    PENDING = "pending_qe_approval"
    ACTIVE = "active"


class Auditor(BaseModel):
    first_name: str
    last_name: str
    system_user: str


# --- User schemas ---

class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    role: str


class UserResponse(BaseModel):
    username: str
    first_name: str
    last_name: str
    role: str

    model_config = {"from_attributes": True}


# --- ProductFamily schemas ---

class ProductFamilyCreate(BaseModel):
    name: str


class ProductFamilyResponse(BaseModel):
    name: str
    status: str
    proposed_by: str
    approved_by: str | None = None

    model_config = {"from_attributes": True}


# --- PartNumber schemas ---

class PartNumberCreate(BaseModel):
    code: str
    description: str
    family_name: str


class PartNumberResponse(BaseModel):
    code: str
    description: str
    family_name: str | None = None
    status: str | None = None
    proposed_by: str | None = None
    approved_by: str | None = None

    model_config = {"from_attributes": True}

# --- Lot schemas ---

class LotCreate(BaseModel):
    lot_id: str
    part_number_code: str
    units: int
    manufacturing_date: date
    status: LotStatus = LotStatus.READY_FOR_AUDIT


class LotResponse(BaseModel):
    batch_id: int
    lot_id: str
    part_number_code: str
    part_number_description: str | None = None
    product_family: str | None = None
    units: int
    manufacturing_date: date
    status: LotStatus
    audited_by: Auditor | None = None
    audited_at: datetime | None = None
    ncr_number: str | None = None
    me_approved_by: str | None = None
    qe_approved_by: str | None = None

    model_config = {"from_attributes": False}