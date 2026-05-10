from app.models.tinh import Tinh

def get_by_id(db, ma_tinh):
    return db.query(Tinh).filter(
        Tinh.ma_tinh == ma_tinh
    ).first()