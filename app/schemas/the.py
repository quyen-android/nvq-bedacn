from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class TheCreate(BaseModel):
    ten_the: str
    ma_loai: UUID


class TheUpdate(BaseModel):
    ten_the: Optional[str] = None
    ma_loai: Optional[UUID] = None


class TheResponse(BaseModel):
    ma_the: UUID
    ten_the: str
    ma_loai: UUID
    ten_loai: Optional[str] = None

    class Config:
        from_attributes = True