from fastapi import APIRouter, Depends, HTTPException, status
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.services import chi_phi_service 
from app.schemas.chi_phi import ChiPhiRequest

router = APIRouter(prefix="/giave", tags=["Giá vé"])

@router.post("/tinh-gia-ve")
def tinh_gia_ve(
    request: ChiPhiRequest,
    db: Session = Depends(get_db)
):
    return chi_phi_service.tinh_gia_ve(
        db,
        request.ma_tinh_di,
        request.ma_tinh_den,
        request.ma_pt
    )