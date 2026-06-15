from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.schemas.chuyen_di import (
    ChuyenDiCreate,
    ChuyenDiUpdate,
    ChuyenDiResponse
)
from app.services.chuyen_di_service import ChuyenDiService


router = APIRouter(
    prefix="/chuyen-di",
    tags=["Chuyến đi"]
)


@router.post(
    "",
    response_model=ChuyenDiResponse
)
def create_chuyen_di(
    data: ChuyenDiCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ChuyenDiService.create_chuyen_di(
            db=db,
            data=data,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.get(
    "",
    response_model=list[ChuyenDiResponse]
)
def get_my_chuyen_dis(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    return ChuyenDiService.get_my_chuyen_dis(
        db=db,
        current_user=current_user
    )


@router.get(
    "/{ma_chuyen_di}",
    response_model=ChuyenDiResponse
)
def get_chuyen_di_detail(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ChuyenDiService.get_chuyen_di_detail(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )


@router.put(
    "/{ma_chuyen_di}",
    response_model=ChuyenDiResponse
)
def update_chuyen_di(
    ma_chuyen_di: UUID,
    data: ChuyenDiUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ChuyenDiService.update_chuyen_di(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            data=data,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


@router.delete(
    "/{ma_chuyen_di}"
)
def delete_chuyen_di(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ChuyenDiService.delete_chuyen_di(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    

@router.put(
    "/{ma_chuyen_di}/complete"
)
def complete_chuyen_di(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ChuyenDiService.complete_chuyen_di(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )