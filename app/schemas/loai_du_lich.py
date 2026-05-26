from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class LoaiDuLichCreate(BaseModel):
    ten_loai: str


class LoaiDuLichUpdate(BaseModel):
    ten_loai: Optional[str] = None


class LoaiDuLichResponse(BaseModel):
    ma_loai_du_lich: UUID
    ten_loai: str

    class Config:
        from_attributes = True