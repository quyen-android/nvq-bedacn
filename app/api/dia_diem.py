from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user_optional
from app.services.public_dia_diem_service import (
    PublicDiaDiemService
)

router = APIRouter(
    prefix="/dia-diem",
    tags=["DiaDiem"]
)

service = PublicDiaDiemService()


@router.get("")
def get_places(
    ma_loai: str | None = Query(None),
    ma_tinh: str | None = Query(None),
    min_price: float | None = Query(None),
    max_price: float | None = Query(None),
    min_rating: float | None = Query(None),
    tag_ids: list[str] | None = Query(None),
    keyword: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    return service.get_places(
        db=db,
        current_user=current_user,
        ma_loai=ma_loai,
        ma_tinh=ma_tinh,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        tag_ids=tag_ids,
        keyword=keyword
    )


@router.get("/{ma_dia_diem}")
def get_place_detail(
    ma_dia_diem: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    return service.get_place_detail(
        db=db,
        ma_dia_diem=ma_dia_diem,
        current_user=current_user
    )