import uuid

from sqlalchemy import Column, Text, String, Integer, Float, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP

from app.db.base import Base


class NhatKyAI(Base):
    __tablename__ = "nhat_ky_ai"

    ma_log = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    ma_nguoi_dung = Column(
        UUID(as_uuid=True),
        ForeignKey("nguoi_dung.ma_nguoi_dung", ondelete="SET NULL"),
        nullable=True
    )

    ma_chuyen_di = Column(
        UUID(as_uuid=True),
        ForeignKey("chuyen_di.ma_chuyen_di", ondelete="CASCADE"),
        nullable=True
    )

    cau_hoi = Column(Text)
    cau_tra_loi = Column(Text)
    ngu_canh = Column(Text)

    model = Column(String(50))
    tokens_su_dung = Column(Integer)
    tg_phan_hoi = Column(Float)

    danh_gia = Column(Integer)

    ngay_tao = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now()
    )