from sqlalchemy import Column, String, ForeignKey, Date, Time, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base

class YeuCauDacBiet(Base):
    __tablename__ = "yeu_cau_dac_biet"

    ma_yeu_cau = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ten_yeu_cau = Column(String(255))

    chuyen_dis = relationship("YeuCauCD", back_populates="yeu_cau")