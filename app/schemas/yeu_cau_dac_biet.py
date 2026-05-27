from pydantic import BaseModel
from typing import Optional


class YeuCauDacBietCreate(BaseModel):
    ten_yeu_cau: str


class YeuCauDacBietUpdate(BaseModel):
    ten_yeu_cau: Optional[str] = None