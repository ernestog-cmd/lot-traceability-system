from datetime import date, datetime
from enum import Enum
from pydantic import BaseModel

class LotStatus(str, Enum):
    READY_FOR_AUDIT = "ready_for_audit"
    IN_AUDIT_PROCESS = "in_audit_process"
    RELEASED = "released"
    HOLD = "hold"


class Auditor(BaseModel):
    first_name: str
    last_name: str
    system_user: str



class PartNumberCreate(BaseModel):
    code: str
    description: str

class PartNumberResponse(BaseModel):
    code: str
    description: str

    model_config = {"from_attributes": True}


class LotCreate(BaseModel):
    lot_id: str
    part_number_code: str
    product_family: str
    units: int
    manufacturing_date: date
    status: LotStatus = LotStatus.READY_FOR_AUDIT

class LotResponse(BaseModel):
    batch_id: int
    lot_id: str
    part_number_code: str
    part_number_description: str | None = None
    product_family: str
    units: int
    manufacturing_date: date
    status: LotStatus
    audited_by: Auditor | None = None
    audited_at: datetime | None = None

    model_config = {"from_attributes": False}

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