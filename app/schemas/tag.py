from pydantic import BaseModel
from uuid import UUID

class TagResponse(BaseModel):
    ten_the: str

    class Config:
        from_attributes = True