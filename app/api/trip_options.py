from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tinh import Tinh
from app.models.phuong_tien import PhuongTien
from app.models.loai_du_lich import LoaiDuLich
from app.models.so_thich_am_thuc import SoThichAmThuc
from app.models.yeu_cau_dac_biet import YeuCauDacBiet


router = APIRouter(
    prefix="/trip-options",
    tags=["Trip Options"]
)


@router.get("")
def get_trip_options(
    db: Session = Depends(get_db)
):
    tinhs = db.query(Tinh).all()
    phuong_tiens = (
        db.query(PhuongTien)
        .filter(PhuongTien.loai == "lien_tinh")
        .all()
    )
    loai_du_lichs = db.query(LoaiDuLich).all()
    so_thichs = db.query(SoThichAmThuc).all()
    yeu_caus = db.query(YeuCauDacBiet).all()

    return {
        "tinhs": [
            {
                "id": str(item.ma_tinh),
                "name": item.ten_tinh
            }
            for item in tinhs
        ],

        "phuong_tiens": [
            {
                "id": str(item.ma_pt),
                "name": item.ten_pt
            }
            for item in phuong_tiens
        ],

        "loai_du_lichs": [
            {
                "id": str(item.ma_loai_du_lich),
                "name": item.ten_loai
            }
            for item in loai_du_lichs
        ],

        "so_thichs": [
            {
                "id": str(item.ma_so_thich),
                "name": item.ten_so_thich
            }
            for item in so_thichs
        ],

        "yeu_caus": [
            {
                "id": str(item.ma_yeu_cau),
                "name": item.ten_yeu_cau
            }
            for item in yeu_caus
        ]
    }