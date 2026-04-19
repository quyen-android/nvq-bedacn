from sqlalchemy import Column, String, Text, Float, Integer, Boolean, Time, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid

from app.db.base import Base


class DiaDiem(Base):
    __tablename__ = "dia_diem"

    ma_dia_diem = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_tinh = Column(UUID(as_uuid=True), ForeignKey("tinh.ma_tinh"))
    ma_loai = Column(UUID(as_uuid=True), ForeignKey("loai_dia_diem.ma_loai"))

    ten = Column(String)
    dia_chi = Column(Text)
    mo_ta = Column(Text)

    kinh_do = Column(Float)
    vi_do = Column(Float)

    gia_trung_binh = Column(Float)

    danh_gia = Column(Float, default=0)
    so_danh_gia = Column(Integer, default=0)

    gio_mo = Column(Time)
    gio_dong = Column(Time)

    website = Column(Text)
    sdt = Column(String)

    trang_thai = Column(Boolean, default=True)
    
    tinh = relationship("Tinh", back_populates="dia_diems")
    loai = relationship("LoaiDiaDiem", back_populates="dia_diems")
    anh = relationship("AnhDiaDiem", back_populates="dia_diem")