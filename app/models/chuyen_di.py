import uuid
from sqlalchemy import Column, String, Date, Integer, DECIMAL, DateTime,ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime, timezone

class ChuyenDi(Base):
    __tablename__ = "chuyen_di"

    ma_chuyen_di = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_pt = Column(UUID(as_uuid=True), ForeignKey("phuong_tien.ma_pt", ondelete="SET NULL"), nullable=True)

    ma_nguoi_dung = Column(UUID(as_uuid=True), ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="CASCADE"))

    ma_tinh_di = Column(UUID(as_uuid=True), ForeignKey("tinh.ma_tinh", ondelete="SET NULL"))

    ma_tinh_den = Column(UUID(as_uuid=True), ForeignKey("tinh.ma_tinh", ondelete="SET NULL"))

    ten_chuyen_di = Column(String(255))

    ngay_di = Column(Date)

    ngay_ve = Column(Date)

    so_nguoi = Column(Integer, default=1)

    ngan_sach = Column(DECIMAL(10, 2))

    trang_thai = Column(String(50))

    nguoi_dung = relationship("User", back_populates="chuyen_dis")

    phuong_tien = relationship("PhuongTien")

    ngay_tao = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ngay_cap_nhat = Column(DateTime(timezone=True), nullable=True)

    tinh_di = relationship("Tinh", foreign_keys=[ma_tinh_di])

    tinh_den = relationship("Tinh", foreign_keys=[ma_tinh_den])

    lich_trinhs = relationship("LichTrinh", back_populates="chuyen_di", cascade="all, delete")

    chi_phi_chuyen_dis = relationship("ChiPhiChuyenDi", back_populates="chuyen_di", cascade="all, delete")

    so_thichs = relationship("SoThichCD", back_populates="chuyen_di", cascade="all, delete")

    loai_du_lichs = relationship("LoaiDuLichCD", back_populates="chuyen_di", cascade="all, delete")

    yeu_caus = relationship("YeuCauCD", back_populates="chuyen_di", cascade="all, delete")