from sqlalchemy import Column, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.db.base import Base

class YeuThich(Base):
    __tablename__ = "yeu_thich"

    ma_nguoi_dung = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.ma_nguoi_dung"), primary_key=True)
    ma_dia_diem = Column(UUID(as_uuid=True), ForeignKey("dia_diem.ma_dia_diem"), primary_key=True)

    ngay_tao = Column(DateTime, default=lambda: datetime.now(timezone.utc))