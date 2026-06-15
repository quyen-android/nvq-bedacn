from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class ChiTietLichTrinhUpdate(BaseModel):
    ma_chi_tiet: Optional[str] = None
    ma_dia_diem: Optional[UUID] = None

    start_time: Optional[str] = None
    end_time: Optional[str] = None

    ma_pt: Optional[UUID] = None

    distance_km: Optional[float] = 0
    number_of_vehicles: Optional[int] = 1
    estimated_transport_cost: Optional[float] = 0


class LichTrinhDayUpdate(BaseModel):
    day: int
    items: list[ChiTietLichTrinhUpdate]


class LichTrinhUpdateRequest(BaseModel):
    days: list[LichTrinhDayUpdate]


class KiemTraDoiPhuongTienRequest(BaseModel):
    ma_pt_moi: UUID
    distance_km: float
    old_cost: float = 0
    so_nguoi: int = 1


class KiemTraDoiPhuongTienRequest(BaseModel):
    ma_pt_moi: UUID
    distance_km: float
    old_cost: float = 0
    so_nguoi: int = 1
    number_of_vehicles: Optional[int] = None