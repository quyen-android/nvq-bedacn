from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class AnhDiaDiem(Base):
    __tablename__ = "anh_dia_diem"

    ma_anh = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_dia_diem = Column(UUID(as_uuid=True), ForeignKey("dia_diem.ma_dia_diem"))

    url = Column(String)
    la_anh_chinh = Column(Boolean, default=False)

    dia_diem = relationship("DiaDiem", back_populates="anh")