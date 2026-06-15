from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel


class ChatbotRequest(BaseModel):
    ma_chuyen_di: UUID
    message: str


class ChatbotResponse(BaseModel):
    answer: str
    itinerary_update: Optional[dict[str, Any]] = None