from uuid import UUID
from pydantic import BaseModel

class ChiPhiRequest(BaseModel):
    ma_chuyen_di: UUID

    ma_tinh_di: UUID | None = None
    ma_tinh_den: UUID | None = None

    ma_pt: UUID | None = None

    ma_dia_diem: UUID | None = None

    so_nguoi: int 
    so_phong: int 