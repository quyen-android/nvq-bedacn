from app.models.chuyen_di import ChuyenDi

def get_by_id(db, ma_chuyen_di):
    return db.query(ChuyenDi).filter(
        ChuyenDi.ma_chuyen_di == ma_chuyen_di
    ).first()