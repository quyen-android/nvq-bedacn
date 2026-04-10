from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
import uuid
from app.db.base import Base

class RefreshToken(Base):
    __tablename__ = "lammoitoken"

    ma_lam_moi = Column(String, primary_key=True, default=lambda:str(uuid.uuid4()))
    ma_nguoi_dung = Column(Integer, ForeignKey("nguoidung.ma_nguoi_dung"))
    ma_token = Column(String, unique=True)
    thoi_gian_het_han = Column(DateTime)
    da_thu_hoi = Column(Boolean, default=False)
    ngay_tao = Column(DateTime, default=datetime.now(timezone.utc))