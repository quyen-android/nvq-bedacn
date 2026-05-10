from sqlalchemy import Column, String, Date, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class LoaiDuLich(Base):
    __tablename__ = "loai_du_lich"

    ma_loai_du_lich = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ten_loai = Column(String(100))

    chuyen_dis = relationship("LoaiDuLichCD", back_populates="loai")