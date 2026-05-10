from sqlalchemy import Column, String, Date, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class ChiPhi(Base):
    __tablename__ = "chi_phi"

    ma_chi_phi = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    loai_chi_phi = Column(String(100))

    chuyen_dis = relationship("ChiPhiChuyenDi", back_populates="chi_phi")