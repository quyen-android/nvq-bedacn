from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.phuong_tien import PhuongTien


router = APIRouter(
    prefix="/phuong-tien",
    tags=["Phương tiện"]
)


@router.get("/local")
def get_local_phuong_tien(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        phuong_tiens = (
            db.query(PhuongTien)
            .filter(PhuongTien.loai != "lien_tinh")
            .all()
        )

        return [
            {
                "id": str(item.ma_pt),
                "name": item.ten_pt,
                "loai": item.loai,
                "toc_do_tb": float(item.toc_do_tb or 0),
                "gia_moi_km": float(item.gia_moi_km or 0),
                "suc_chua": item.suc_chua
            }
            for item in phuong_tiens
        ]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Lỗi lấy phương tiện địa phương: {str(e)}"
        )