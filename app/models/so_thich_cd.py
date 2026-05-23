from sqlalchemy import Column, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base


class SoThichCD(Base):
    __tablename__ = "so_thich_cd"

    ma_chuyen_di = Column(UUID(as_uuid=True), ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"), primary_key=True)

    ma_so_thich = Column(UUID(as_uuid=True), ForeignKey("so_thich_am_thuc.ma_so_thich", ondelete="CASCADE"), primary_key=True)

    chuyen_di = relationship("ChuyenDi", back_populates="so_thichs")

    so_thich = relationship("SoThichAmThuc", back_populates="chuyen_dis")