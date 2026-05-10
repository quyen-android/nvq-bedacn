from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class LichTrinh(Base):
    __tablename__ = "lich_trinh"

    ma_lich_trinh = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_chuyen_di = Column(UUID(as_uuid=True), ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"))

    tieu_de = Column(String(255))
    ngay = Column(Date)
    chi_phi_ngay = Column(DECIMAL(10, 2))

    trang_thai = Column(String(50))

    # relationship
    chuyen_di = relationship("ChuyenDi", back_populates="lich_trinhs")
    chi_tiets = relationship("ChiTietLichTrinh", back_populates="lich_trinh", cascade="all, delete")