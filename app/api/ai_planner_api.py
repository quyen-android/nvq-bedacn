from fastapi import APIRouter
from sqlalchemy.orm import Session

from app.db.session import get_db

from fastapi import Depends

from app.services.ai_planner_service import (
    AIPlannerService
)

router = APIRouter(
    prefix="/ai-planner",
    tags=["AI Planner"]
)


@router.post("/{ma_chuyen_di}")
def generate_plan(
    ma_chuyen_di: str,
    db: Session = Depends(get_db)
):

    return AIPlannerService.generate_plan(
        db,
        ma_chuyen_di
    )