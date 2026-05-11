from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL,Float, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class PhuongTien(Base):
    __tablename__ = "phuong_tien"

    ma_pt = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ten_pt = Column(String(100))
    loai = Column(String(50))

    suc_chua= Column(Integer, default=1)
    gia_moi_km = Column(DECIMAL(10, 2))

    toc_do_tb = Column(Float)