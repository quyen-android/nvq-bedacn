from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from app.db.base import Base


class SoThichAmThuc(Base):
    __tablename__ = "so_thich_am_thuc"

    ma_so_thich = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ten_so_thich = Column(String(100), nullable=False)

    chuyen_dis = relationship("SoThichCD", back_populates="so_thich")