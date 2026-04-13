from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone
from app.db.base import Base
import uuid
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
    __tablename__ = "nguoi_dung"

    ma_nguoi_dung = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ten_nguoi_dung = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    mat_khau = Column(String, nullable=True)
    sdt = Column(String, nullable=True)
    dia_chi = Column(String, nullable=True)
    anh_url = Column(String, nullable=True)
    quyen = Column(String, default="user")
    trang_thai = Column(Boolean, default=True)
    dn_lan_cuoi = Column(DateTime(timezone=True), nullable=True)
    ngay_tao = Column(DateTime, default=lambda: datetime.now(timezone.utc))