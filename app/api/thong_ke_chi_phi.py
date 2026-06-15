from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services.thong_ke_chi_phi_service import ThongKeChiPhiService


router = APIRouter(
    prefix="/thong-ke-chi-phi",
    tags=["Thống kê chi phí"]
)


@router.get("/{ma_chuyen_di}")
def thong_ke_chi_phi_chuyen_di(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        return ThongKeChiPhiService.thong_ke_theo_chuyen_di(
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
            detail=f"Lỗi thống kê chi phí: {str(e)}"
        )