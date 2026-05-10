from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class YeuCauCD(Base):
    __tablename__ = "yeu_cau_cd"

    ma_chuyen_di = Column(UUID(as_uuid=True), ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"), primary_key=True)
    ma_yeu_cau = Column(UUID(as_uuid=True), ForeignKey("yeu_cau_dac_biet.ma_yeu_cau", ondelete="CASCADE"), primary_key=True)

    # relationship
    chuyen_di = relationship("ChuyenDi", back_populates="yeu_caus")
    yeu_cau = relationship("YeuCauDacBiet", back_populates="chuyen_dis")