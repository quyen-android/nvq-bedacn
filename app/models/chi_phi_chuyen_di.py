from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class ChiPhiChuyenDi(Base):
    __tablename__ = "chi_phi_chuyen_di"

    ma_chuyen_di = Column(UUID(as_uuid=True), ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"), primary_key=True)
    ma_chi_phi = Column(UUID(as_uuid=True), ForeignKey("chi_phi.ma_chi_phi", ondelete="CASCADE"), primary_key=True)

    so_tien = Column(DECIMAL(10, 2))

    # relationship
    chuyen_di = relationship(
        "ChuyenDi",
        back_populates="chi_phi_chuyen_dis"
    )

    chi_phi = relationship(
        "ChiPhi",
        back_populates="chi_phi_chuyen_dis"
    )