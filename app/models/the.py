from sqlalchemy import Column, String, ForeignKey
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid 

class The(Base):
    __tablename__ = "the"

    ma_nguoi_dung = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ten_the = Column(String)

    ma_loai = Column(UUID(as_uuid=True), ForeignKey("loai_dia_diem.ma_loai"))