from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.loai_du_lich import LoaiDuLichCreate, LoaiDuLichUpdate
from app.services.loai_du_lich_service import LoaiDuLichService
from app.core.deps import require_role


router = APIRouter(
    prefix="/loai-du-lich",
    tags=["Loại du lịch"]
)


def serialize_item(item):
    return {
        "ma_loai_du_lich": item.ma_loai_du_lich,
        "ten_loai": item.ten_loai
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    items = LoaiDuLichService.get_all(db)

    return [
        serialize_item(item)
        for item in items
    ]


@router.get("/{ma_loai_du_lich}")
def get_by_id(
    ma_loai_du_lich: UUID,
    db: Session = Depends(get_db)
):
    try:
        item = LoaiDuLichService.get_by_id(
            db,
            ma_loai_du_lich
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: LoaiDuLichCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = LoaiDuLichService.create(
            db,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_loai_du_lich}")
def update(
    ma_loai_du_lich: UUID,
    data: LoaiDuLichUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = LoaiDuLichService.update(
            db,
            ma_loai_du_lich,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_loai_du_lich}")
def delete(
    ma_loai_du_lich: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        return LoaiDuLichService.delete(
            db,
            ma_loai_du_lich
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )