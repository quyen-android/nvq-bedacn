from pydantic import BaseModel
from typing import Optional
from uuid import UUID


class KhungGioVangCreate(BaseModel):
    ma_dia_diem: UUID
    thang_bat_dau: int
    thang_ket_thuc: int
    gio_bat_dau: str
    gio_ket_thuc: str


class KhungGioVangUpdate(BaseModel):
    ma_dia_diem: Optional[UUID] = None
    thang_bat_dau: Optional[int] = None
    thang_ket_thuc: Optional[int] = None
    gio_bat_dau: Optional[str] = None
    gio_ket_thuc: Optional[str] = None