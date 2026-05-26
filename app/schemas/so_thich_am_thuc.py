from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class SoThichAmThucCreate(BaseModel):
    ten_so_thich: str


class SoThichAmThucUpdate(BaseModel):
    ten_so_thich: Optional[str] = None