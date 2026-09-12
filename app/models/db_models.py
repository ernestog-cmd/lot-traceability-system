from sqlalchemy import Column, String, Integer, Date, DateTime, ForeignKey, UniqueConstraint
from app.database import Base


class ProductFamily(Base):
    __tablename__ = "product_families"

    name = Column(String, primary_key=True, index=True)
    status = Column(String, nullable=False, default="pending_qe_approval")
    proposed_by = Column(String, ForeignKey("users.username"), nullable=False)
    approved_by = Column(String, ForeignKey("users.username"), nullable=True)


class PartNumber(Base):
    __tablename__ = "part_numbers"

    code = Column(String, primary_key=True, index=True)
    description = Column(String, nullable=False)
    family_name = Column(String, ForeignKey("product_families.name"), nullable=False)
    status = Column(String, nullable=False, default="pending_qe_approval")
    proposed_by = Column(String, ForeignKey("users.username"), nullable=False)
    approved_by = Column(String, ForeignKey("users.username"), nullable=True)


class LotDB(Base):
    __tablename__ = "lots"

    batch_id = Column(Integer, primary_key=True, autoincrement=True)
    lot_id = Column(String, nullable=False, index=True)
    part_number_code = Column(String, ForeignKey("part_numbers.code"), nullable=False)
    product_family = Column(String, nullable=False)
    units = Column(Integer, nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="ready_for_audit")
    audited_by_first_name = Column(String, nullable=True)
    audited_by_last_name = Column(String, nullable=True)
    audited_by_system_user = Column(String, nullable=True)
    audited_at = Column(DateTime, nullable=True)
    ncr_number = Column(String, nullable=True)
    me_approved_by = Column(String, ForeignKey("users.username"), nullable=True)
    qe_approved_by = Column(String, ForeignKey("users.username"), nullable=True)

    __table_args__ = (
        UniqueConstraint("lot_id", "part_number_code", name="uq_lot_part_number"),
    )


class UserDB(Base):
    __tablename__ = "users"

    username = Column(String, primary_key=True, index=True)
    hashed_password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(String, nullable=False)