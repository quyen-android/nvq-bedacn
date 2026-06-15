from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.services.ai_planner_service import AIPlannerService


router = APIRouter(
    prefix="/ai-planner",
    tags=["AI Planner"]
)


@router.post("/{ma_chuyen_di}")
def generate_ai_plan(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db)
):
    try:
        return AIPlannerService.generate_and_save(
            db=db,
            ma_chuyen_di=ma_chuyen_di
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi tạo lịch trình AI: {str(e)}"
        )