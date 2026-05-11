from uuid import UUID
from pydantic import BaseModel


class ChiPhiRequest(BaseModel):
    ma_chuyen_di: UUID