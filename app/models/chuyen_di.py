import uuid
from sqlalchemy import Column, String, Date, Integer, DECIMAL, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChuyenDi(Base):
    __tablename__ = "chuyen_di"

    ma_chuyen_di = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_pt = Column(
        UUID(as_uuid=True),
        ForeignKey("phuong_tien.ma_pt", ondelete="SET NULL"),
        nullable=True
    )

    ma_nguoi_dung = Column(
        UUID(as_uuid=True),
        ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="CASCADE")
    )

    ma_tinh_di = Column(
        UUID(as_uuid=True),
        ForeignKey("tinh.ma_tinh", ondelete="SET NULL"),
    )

    ma_tinh_den = Column(
        UUID(as_uuid=True),
        ForeignKey("tinh.ma_tinh", ondelete="SET NULL"),
    )

    ten_chuyen_di = Column(String(255))

    ngay_di = Column(Date)
    ngay_ve = Column(Date)

    so_nguoi = Column(Integer, default=1)
    ngan_sach = Column(DECIMAL(10, 2))

    # user
    nguoi_dung = relationship("NguoiDung", back_populates="chuyen_dis")

    # phương tiện global
    phuong_tien = relationship("PhuongTien")

    # tỉnh
    tinh_di = relationship("Tinh", foreign_keys=[ma_tinh_di])
    tinh_den = relationship("Tinh", foreign_keys=[ma_tinh_den])

    # lịch trình
    lich_trinhs = relationship(
        "LichTrinh",
        back_populates="chuyen_di",
        cascade="all, delete"
    )