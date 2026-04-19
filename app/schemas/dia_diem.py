from uuid import UUID
from pydantic import BaseModel

class DiaDiemResponse(BaseModel):
    ten: str
    danh_gia: float
    gia: float
    is_favorite: bool

    class Config:
        from_attributes = True