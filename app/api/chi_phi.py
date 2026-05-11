from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services import chi_phi_service 
from app.schemas.chi_phi import ChiPhiRequest
from app.services import chi_phi_service
from uuid import UUID

router = APIRouter(prefix="/giave", tags=["Giá vé"])

@router.post("/tinh-gia-ve")
def tinh_gia_ve(
    request: ChiPhiRequest,
    db: Session = Depends(get_db)
):
    return chi_phi_service.tinh_gia_di_chuyen_lien_tinh(
        db,
        request.ma_chuyen_di
    )

@router.put("/so-xe")
def update_so_xe(
    ma_ct: UUID,
    so_luong_pt: int,
    db: Session = Depends(get_db)
):
    return (
        chi_phi_service
        .update_so_luong_pt(
            db,
            ma_ct,
            so_luong_pt
        )
    )

@router.put(
    "/tinh-chi-phi/{ma_chuyen_di}/{ma_lich_trinh}"
)
def tinh_chi_phi_di_chuyen_dia_phuong(
    ma_chuyen_di: UUID,
    ma_lich_trinh: UUID,
    db: Session = Depends(get_db)
):
    try:

        result = (
            chi_phi_service
            .tinh_chi_phi_di_chuyen_dia_phuong(
                db=db,
                ma_chuyen_di=ma_chuyen_di,
                ma_lich_trinh=ma_lich_trinh
            )
        )

        return {
            "success": True,
            "message": (
                "Tính chi phí thành công"
            ),
            "data": result
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
@router.get(
    "/tong-chi-phi-di-chuyen/{ma_chuyen_di}"
)
def tinh_tong_chi_phi_di_chuyen(
    ma_chuyen_di: UUID,
    db: Session = Depends(get_db)
):
    try:

        result = (
            chi_phi_service
            .tinh_tong_chi_phi_di_chuyen(
                db,
                ma_chuyen_di
            )
        )

        return {
            "success": True,
            "data": result
        }

    except ValueError as e:

        raise HTTPException(
            status_code=404,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )