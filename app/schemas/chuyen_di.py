from uuid import UUID
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel


class ChuyenDiCreate(BaseModel):
    ma_pt_di: UUID
    ma_pt_ve: UUID

    ma_tinh_di: UUID
    ma_tinh_den: UUID

    ten_chuyen_di: str

    ngay_di: date
    ngay_ve: date

    so_nguoi: int
    ngan_sach: Decimal

    loai_du_lich_ids: List[UUID] = []
    so_thich_ids: List[UUID] = []
    yeu_cau_ids: List[UUID] = []


class ChuyenDiUpdate(BaseModel):
    ngay_ve: Optional[date] = None
    ngan_sach: Optional[Decimal] = None
    trang_thai: Optional[str] = None


class ChuyenDiResponse(BaseModel):
    ma_chuyen_di: UUID

    ma_pt_di: Optional[UUID] = None
    ma_pt_ve: Optional[UUID] = None

    ma_nguoi_dung: UUID

    ma_tinh_di: Optional[UUID] = None
    ma_tinh_den: Optional[UUID] = None

    ten_chuyen_di: Optional[str] = None

    ngay_di: Optional[date] = None
    ngay_ve: Optional[date] = None

    so_nguoi: Optional[int] = None
    ngan_sach: Optional[Decimal] = None

    trang_thai: Optional[str] = None

    ngay_tao: Optional[datetime] = None
    ngay_cap_nhat: Optional[datetime] = None

    class Config:
        from_attributes = True