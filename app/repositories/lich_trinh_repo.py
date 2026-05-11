from app.models.lich_trinh import LichTrinh
from app.models.chuyen_di import ChuyenDi

def get_by_id(db, ma_lich_trinh):
    return db.query(LichTrinh).filter(
        LichTrinh.ma_lich_trinh == ma_lich_trinh
    ).first()

def get_by_chuyen_di(
    db,
    ma_chuyen_di
):
    return (
        db.query(LichTrinh)
        .filter(
            LichTrinh.ma_chuyen_di == ma_chuyen_di
        )
        .all()
    )