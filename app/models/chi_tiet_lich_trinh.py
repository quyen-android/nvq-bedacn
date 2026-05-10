import uuid
from sqlalchemy import Column, Time, Float, DECIMAL, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class ChiTietLichTrinh(Base):
    __tablename__ = "chi_tiet_lich_trinh"

    ma_ct = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    ma_lich_trinh = Column(
        UUID(as_uuid=True),
        ForeignKey("lich_trinh.ma_lich_trinh", ondelete="CASCADE")
    )

    ma_dia_diem = Column(
        UUID(as_uuid=True),
        ForeignKey("dia_diem.ma_dia_diem", ondelete="SET NULL"),
        nullable=True
    )

    gio_bat_dau = Column(Time)
    gio_ket_thuc = Column(Time)

    # 🚗 phương tiện local
    ma_pt = Column(
        UUID(as_uuid=True),
        ForeignKey("phuong_tien.ma_pt", ondelete="SET NULL"),
        nullable=True
    )

    # 📏 khoảng cách (km)
    khoang_cach = Column(Float)

    # 💸 giá
    gia = Column(DECIMAL(10, 2))

    # ======================
    # 🔗 RELATIONSHIP
    # ======================

    lich_trinh = relationship("LichTrinh", back_populates="chi_tiets")

    dia_diem = relationship("DiaDiem")

    phuong_tien = relationship("PhuongTien")