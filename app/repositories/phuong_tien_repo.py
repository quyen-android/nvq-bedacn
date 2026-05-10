from app.models.phuong_tien import PhuongTien

def get_gia_km(db, ma_pt):
    return db.query(PhuongTien).filter(
        PhuongTien.ma_pt == ma_pt
    ).first()