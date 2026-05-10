from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class LoaiDuLichCD(Base):
    __tablename__ = "loai_du_lich_cd"

    ma_chuyen_di = Column(UUID(as_uuid=True), ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"), primary_key=True)
    ma_loai_du_lich = Column(UUID(as_uuid=True), ForeignKey("loai_du_lich.ma_loai_du_lich", ondelete="CASCADE"), primary_key=True)

    # relationship
    chuyen_di = relationship("ChuyenDi", back_populates="loai_du_lichs")
    loai = relationship("LoaiDuLich", back_populates="chuyen_dis")