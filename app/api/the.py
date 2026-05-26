from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.schemas.the import TheCreate, TheUpdate
from app.services.the_service import TheService
from app.core.deps import require_role


router = APIRouter(
    prefix="/the",
    tags=["Thẻ"]
)


def serialize_the(the):
    return {
        "ma_the": the.ma_the,
        "ten_the": the.ten_the,
        "ma_loai": the.ma_loai,
        "ten_loai": (
            the.loai.ten_loai
            if the.loai
            else None
        )
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    thes = TheService.get_all(db)

    return [
        serialize_the(the)
        for the in thes
    ]


@router.get("/loai/{ma_loai}")
def get_by_loai(
    ma_loai: UUID,
    db: Session = Depends(get_db)
):
    thes = TheService.get_by_loai(
        db,
        ma_loai
    )

    return [
        serialize_the(the)
        for the in thes
    ]


@router.get("/{ma_the}")
def get_by_id(
    ma_the: UUID,
    db: Session = Depends(get_db)
):
    try:
        the = TheService.get_by_id(
            db,
            ma_the
        )

        return serialize_the(the)

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.post("")
def create(
    data: TheCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        the = TheService.create(
            db,
            data
        )

        return serialize_the(the)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.put("/{ma_the}")
def update(
    ma_the: UUID,
    data: TheUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        the = TheService.update(
            db,
            ma_the,
            data
        )

        return serialize_the(the)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete("/{ma_the}")
def delete(
    ma_the: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    try:
        return TheService.delete(
            db,
            ma_the
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )