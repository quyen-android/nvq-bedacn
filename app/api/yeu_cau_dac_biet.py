from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.yeu_cau_dac_biet import (
    YeuCauDacBietCreate,
    YeuCauDacBietUpdate
)
from app.services.yeu_cau_dac_biet_service import YeuCauDacBietService
from app.core.deps import require_role


router = APIRouter(
    prefix="/yeu-cau-dac-biet",
    tags=["Yêu cầu đặc biệt"]
)


def serialize_item(item):
    return {
        "ma_yeu_cau": item.ma_yeu_cau,
        "ten_yeu_cau": item.ten_yeu_cau
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    items = YeuCauDacBietService.get_all(db)

    return [
        serialize_item(item)
        for item in items
    ]


@router.get("/{ma_yeu_cau}")
def get_by_id(
    ma_yeu_cau: UUID,
    db: Session = Depends(get_db)
):
    try:
        item = YeuCauDacBietService.get_by_id(
            db,
            ma_yeu_cau
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: YeuCauDacBietCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = YeuCauDacBietService.create(
            db,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_yeu_cau}")
def update(
    ma_yeu_cau: UUID,
    data: YeuCauDacBietUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = YeuCauDacBietService.update(
            db,
            ma_yeu_cau,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_yeu_cau}")
def delete(
    ma_yeu_cau: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        return YeuCauDacBietService.delete(
            db,
            ma_yeu_cau
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )