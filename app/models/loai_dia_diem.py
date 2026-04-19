from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid 

class LoaiDiaDiem(Base):
    __tablename__ = "loai_dia_diem"

    ma_loai = Column(UUID(as_uuid=True), primary_key=True,default=uuid.uuid4)
    ten_loai = Column(String)

    dia_diems = relationship("DiaDiem", back_populates="loai")