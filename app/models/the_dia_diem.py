from sqlalchemy import Column, ForeignKey
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid 

class TheDiaDiem(Base):
    __tablename__ = "the_dia_diem"

    ma_dia_diem = Column(UUID(as_uuid=True), ForeignKey("dia_diem.ma_dia_diem"), primary_key=True, default=uuid.uuid4)
    ma_the = Column(UUID(as_uuid=True), ForeignKey("the.ma_the"), primary_key=True)
    dia_diem = relationship("DiaDiem",back_populates="the_dia_diems")

    the = relationship("The", back_populates="the_dia_diems")
        