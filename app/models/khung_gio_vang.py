import uuid

from sqlalchemy import (
    Column,
    Integer,
    Time,
    ForeignKey,
    TIMESTAMP
)

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

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
        ForeignKey(
            "dia_diem.ma_dia_diem",
            ondelete="CASCADE"
        ),
        nullable=False
    )

    thang_bat_dau = Column(
        Integer,
        nullable=False
    )

    thang_ket_thuc = Column(
        Integer,
        nullable=False
    )

    gio_bat_dau = Column(
        Time,
        nullable=False
    )

    gio_ket_thuc = Column(
        Time,
        nullable=False
    )

    ngay_ap_dung = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    dia_diem = relationship(
        "DiaDiem",
        back_populates="khung_gio_vangs"
    )