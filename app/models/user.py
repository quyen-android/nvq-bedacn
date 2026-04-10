from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone
from app.db.base import Base

class User(Base):
    __tablename__ = "nguoidung"

    ma_nguoi_dung = Column(Integer, primary_key=True, index=True)
    ten_nguoi_dung = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False, index=True)
    mat_khau = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True)
    sdt = Column(String, nullable=True)
    dia_chi = Column(String, nullable=True)
    anh_url = Column(String, nullable=True)
    quyen = Column(String, default="user")
    trang_thai = Column(Boolean, default=True)
    dn_lan_cuoi = Column(DateTime, nullable=True)
    da_xac_thuc = Column(Boolean, default=False)
    ngay_tao = Column(DateTime, default=datetime.now(timezone.utc))