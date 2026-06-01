from pydantic import BaseModel
from typing import Optional


class TinhCreate(BaseModel):
    ten_tinh: str
    quoc_gia: str

    kinh_do: float
    vi_do: float


class TinhUpdate(BaseModel):
    ten_tinh: Optional[str] = None
    quoc_gia: Optional[str] = None

    kinh_do: Optional[float] = None
    vi_do: Optional[float] = None