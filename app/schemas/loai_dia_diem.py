from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class LoaiDiaDiemCreate(BaseModel):
    ten_loai: str


class LoaiDiaDiemUpdate(BaseModel):
    ten_loai: Optional[str] = None


class LoaiDiaDiemResponse(BaseModel):
    ma_loai: UUID
    ten_loai: str

    class Config:
        from_attributes = True