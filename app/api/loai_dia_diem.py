from fastapi import (
    APIRouter,
    Depends,
    HTTPException
)

from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db

from app.schemas.loai_dia_diem import (
    LoaiDiaDiemCreate,
    LoaiDiaDiemUpdate
)

from app.services.loai_dia_diem_service import (
    LoaiDiaDiemService
)

from app.core.deps import (
    require_role
)

router = APIRouter(
    prefix="/loai-dia-diem",
    tags=["Loại địa điểm"]
)


def serialize_loai(loai):
    return {
        "ma_loai": loai.ma_loai,
        "ten_loai": loai.ten_loai
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    loais = (
        LoaiDiaDiemService.get_all(db)
    )

    return [
        serialize_loai(loai)
        for loai in loais
    ]


@router.get("/{ma_loai}")
def get_by_id(
    ma_loai: UUID,
    db: Session = Depends(get_db)
):
    try:
        loai = (
            LoaiDiaDiemService.get_by_id(
                db,
                ma_loai
            )
        )

        return serialize_loai(loai)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: LoaiDiaDiemCreate,
    db: Session = Depends(get_db),
    admin=Depends(
        require_role("admin")
    )
):
    try:
        loai = (
            LoaiDiaDiemService.create(
                db,
                data
            )
        )

        return serialize_loai(loai)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_loai}")
def update(
    ma_loai: UUID,
    data: LoaiDiaDiemUpdate,
    db: Session = Depends(get_db),
    admin=Depends(
        require_role("admin")
    )
):
    try:
        loai = (
            LoaiDiaDiemService.update(
                db,
                ma_loai,
                data
            )
        )

        return serialize_loai(loai)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_loai}")
def delete(
    ma_loai: UUID,
    db: Session = Depends(get_db),
    admin=Depends(
        require_role("admin")
    )
):
    try:
        return (
            LoaiDiaDiemService.delete(
                db,
                ma_loai
            )
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )