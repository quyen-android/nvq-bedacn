from pydantic import BaseModel
from uuid import UUID
from datetime import date
from decimal import Decimal
from typing import List, Optional


class ChuyenDiCreate(BaseModel):
    ten_chuyen_di: str
    ma_tinh_di: UUID
    ma_tinh_den: UUID
    ma_pt: UUID

    ngay_di: date
    ngay_ve: date

    so_nguoi: int
    ngan_sach: Decimal

    loai_du_lich_ids: Optional[List[UUID]] = []
    so_thich_ids: Optional[List[UUID]] = []
    yeu_cau_ids: Optional[List[UUID]] = []