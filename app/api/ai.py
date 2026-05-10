from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.ai import GenerateItineraryRequest
from app.services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post("/itinerary")
def generate_itinerary(
    request: GenerateItineraryRequest,
    db: Session = Depends(get_db)
):
    return AIService.generate_itinerary(db, request)