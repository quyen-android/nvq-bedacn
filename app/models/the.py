from sqlalchemy import Column, String, ForeignKey
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid 

class The(Base):
    __tablename__ = "the"

    ma_the = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ten_the = Column(String)

    ma_loai = Column(UUID(as_uuid=True), ForeignKey("loai_dia_diem.ma_loai"))

    loai = relationship("LoaiDiaDiem",back_populates="thes")

    dia_diems = relationship("DiaDiem", secondary="the_dia_diem", back_populates="thes")
    the_dia_diems = relationship("TheDiaDiem", back_populates="the")