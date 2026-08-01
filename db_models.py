from sqlalchemy import Column, String, Integer, Date, DateTime
from database import Base


class LotDB(Base):
    __tablename__="Lots"

    id = Column(String, primary_key=True, index=True)
    part_number = Column(String, nullable=False)
    description = Column(String, nullable=False)
    product_family = Column(String, nullable=False)
    units = Column(Integer, nullable=False)
    manufacturing_date = Column(Date, nullable=False)
    status = Column(String, nullable=False, default="ready_for_audit")
    audited_by_first_name = Column(String, nullable=True)
    audited_by_last_name = Column(String, nullable=True)
    audited_by_system_user = Column(String, nullable=True)
    audited_at = Column(DateTime, nullable=True)
