from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.schemas.lich_trinh import (
    LichTrinhUpdateRequest,
    KiemTraDoiPhuongTienRequest
)
from app.services.lich_trinh_service import LichTrinhService


router = APIRouter(
    prefix="/lich-trinh",
    tags=["Lịch trình"]
)

@router.post("/actions/kiem-tra-doi-phuong-tien")
def kiem_tra_doi_phuong_tien(
    data: KiemTraDoiPhuongTienRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return LichTrinhService.kiem_tra_doi_phuong_tien(
            db=db,
            data=data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    
@router.get("/{ma_chuyen_di}")
def get_lich_trinh_by_chuyen_di(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return LichTrinhService.get_by_chuyen_di(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

    except ValueError as e:
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy lịch trình: {str(e)}"
        )


@router.put("/{ma_chuyen_di}")
def update_lich_trinh_by_chuyen_di(
    ma_chuyen_di: UUID,
    data: LichTrinhUpdateRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return LichTrinhService.update_by_chuyen_di(
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

    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi cập nhật lịch trình: {str(e)}"
        )


@router.post("/kiem-tra-doi-phuong-tien")
def kiem_tra_doi_phuong_tien(
    data: KiemTraDoiPhuongTienRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return LichTrinhService.kiem_tra_doi_phuong_tien(
            db=db,
            data=data
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi kiểm tra đổi phương tiện: {str(e)}"
        )