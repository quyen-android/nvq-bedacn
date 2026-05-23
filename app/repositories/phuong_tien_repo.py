from app.models.phuong_tien import PhuongTien

def get_by_id(db, ma_pt):
    return db.query(PhuongTien).filter(
        PhuongTien.ma_pt == ma_pt
    ).first()

def get_all_local_vehicles(db):
    return (
        db.query(PhuongTien)
        .filter(
            PhuongTien.loai == "dia_phuong"
        )
        .all()
    )