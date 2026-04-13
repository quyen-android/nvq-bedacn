from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey
from datetime import datetime, timezone
import uuid
from app.db.base import Base
from sqlalchemy.dialects.postgresql import UUID

class RefreshToken(Base):
    __tablename__ = "lam_moi_token"

    ma_lam_moi = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ma_nguoi_dung = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.ma_nguoi_dung"),nullable=False)
    ma_token = Column(String, unique=True)
    thoi_gian_het_han = Column(DateTime(timezone=True))
    da_thu_hoi = Column(Boolean, default=False)
    ngay_tao = Column(DateTime, default=datetime.now(timezone.utc))