from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.tinh import TinhCreate, TinhUpdate
from app.services.tinh_service import TinhService
from app.core.deps import require_role


router = APIRouter(
    prefix="/tinh",
    tags=["Tỉnh"]
)


def serialize_tinh(tinh):
    return {
        "ma_tinh": tinh.ma_tinh,
        "ten_tinh": tinh.ten_tinh,
        "quoc_gia": tinh.quoc_gia,
        "kinh_do": tinh.kinh_do,
        "vi_do": tinh.vi_do
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    tinhs = TinhService.get_all(db)

    return [
        serialize_tinh(tinh)
        for tinh in tinhs
    ]


@router.get("/{ma_tinh}")
def get_by_id(
    ma_tinh: UUID,
    db: Session = Depends(get_db)
):
    try:
        tinh = TinhService.get_by_id(db, ma_tinh)
        return serialize_tinh(tinh)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: TinhCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        tinh = TinhService.create(db, data)
        return serialize_tinh(tinh)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_tinh}")
def update(
    ma_tinh: UUID,
    data: TinhUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        tinh = TinhService.update(db, ma_tinh, data)
        return serialize_tinh(tinh)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_tinh}")
def delete(
    ma_tinh: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        return TinhService.delete(db, ma_tinh)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )