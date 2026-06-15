from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chuyen_di import ChuyenDi
from app.services.thoi_tiet_service import ThoiTietService


router = APIRouter(
    prefix="/thoi-tiet",
    tags=["Thời tiết"]
)


def check_owner(db, ma_chuyen_di, current_user):
    chuyen_di = (
        db.query(ChuyenDi)
        .filter(
            ChuyenDi.ma_chuyen_di == ma_chuyen_di,
            ChuyenDi.ma_nguoi_dung == current_user.ma_nguoi_dung
        )
        .first()
    )

    if not chuyen_di:
        raise ValueError("Không tìm thấy chuyến đi")

    return chuyen_di


@router.get("/chuyen-di/{ma_chuyen_di}")
def get_weather_by_trip(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        check_owner(db, ma_chuyen_di, current_user)

        return ThoiTietService.update_trip_weather(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            force=False
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.post("/refresh/{ma_chuyen_di}")
def refresh_weather_by_trip(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        check_owner(db, ma_chuyen_di, current_user)

        return ThoiTietService.update_trip_weather(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            force=True
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )