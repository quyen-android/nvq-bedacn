from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.so_thich_am_thuc import (
    SoThichAmThucCreate,
    SoThichAmThucUpdate
)
from app.services.so_thich_am_thuc_service import SoThichAmThucService
from app.core.deps import require_role


router = APIRouter(
    prefix="/so-thich-am-thuc",
    tags=["Sở thích ẩm thực"]
)


def serialize_item(item):
    return {
        "ma_so_thich": item.ma_so_thich,
        "ten_so_thich": item.ten_so_thich
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    items = SoThichAmThucService.get_all(db)

    return [
        serialize_item(item)
        for item in items
    ]


@router.get("/{ma_so_thich}")
def get_by_id(
    ma_so_thich: UUID,
    db: Session = Depends(get_db)
):
    try:
        item = SoThichAmThucService.get_by_id(
            db,
            ma_so_thich
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: SoThichAmThucCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = SoThichAmThucService.create(
            db,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_so_thich}")
def update(
    ma_so_thich: UUID,
    data: SoThichAmThucUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        item = SoThichAmThucService.update(
            db,
            ma_so_thich,
            data
        )

        return serialize_item(item)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_so_thich}")
def delete(
    ma_so_thich: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        return SoThichAmThucService.delete(
            db,
            ma_so_thich
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )