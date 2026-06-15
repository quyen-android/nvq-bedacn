import uuid

from sqlalchemy import Column, Date, Float, String, ForeignKey, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from app.db.base import Base


class ThoiTietChuyenDi(Base):
    __tablename__ = "thoi_tiet_chuyen_di"

    ma_thoi_tiet = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    ma_chuyen_di = Column(
        UUID(as_uuid=True),
        ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"),
        nullable=False
    )

    ngay = Column(Date, nullable=False)

    nhiet_do = Column(Float)
    nhiet_do_min = Column(Float)
    nhiet_do_max = Column(Float)

    mo_ta = Column(String(255))
    icon = Column(String(100))

    ngay_cap_nhat = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )