import uuid
from sqlalchemy import Column, String, Integer, Time, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


class KhungGioVang(Base):
    __tablename__ = "khung_gio_vang"

    ma_khung_gio = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    ma_dia_diem = Column(
        UUID(as_uuid=True),
        ForeignKey("dia_diem.ma_dia_diem", ondelete="CASCADE")
    )

    mua_du_lich = Column(String(20))

    thang_bat_dau = Column(Integer)
    thang_ket_thuc = Column(Integer)

    gio_bat_dau = Column(Time)
    gio_ket_thuc = Column(Time)

    ngay_ap_dung = Column(TIMESTAMP(timezone=True))

    dia_diem = relationship(
        "DiaDiem",
        back_populates="khung_gio_vangs"
    )