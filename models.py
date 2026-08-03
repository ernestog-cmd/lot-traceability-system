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

class Lot(BaseModel):
    id: str
    part_number: str
    description: str
    product_family: str
    units: int
    manufacturing_date: date
    status: LotStatus = LotStatus.READY_FOR_AUDIT
    audited_by: Auditor | None = None
    audited_at: datetime | None = None


class LotResponse(BaseModel):
    id: str
    part_number: str
    description: str
    product_family: str
    units: int
    manufacturing_date: date
    status: LotStatus
    audited_by: Auditor | None = None
    audited_at: datetime | None = None

    model_config = {"from_attributes": True}

