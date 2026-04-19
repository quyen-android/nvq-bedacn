from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
import uuid

class Tinh(Base):
    __tablename__ = "tinh"

    ma_tinh = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ten_tinh = Column(String)

    dia_diems = relationship("DiaDiem", back_populates="tinh")