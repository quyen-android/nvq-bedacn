from sqlalchemy import Column, ForeignKey
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid 

class TheDiaDiem(Base):
    __tablename__ = "the_dia_diem"

    ma_dia_diem = Column(UUID(as_uuid=True), ForeignKey("dia_diem.ma_dia_diem"), primary_key=True, default=uuid.uuid4)
    ma_the = Column(UUID(as_uuid=True), ForeignKey("the.ma_the"), primary_key=True)