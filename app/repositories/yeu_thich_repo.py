from sqlalchemy.orm import Session
from app.models import YeuThich, DiaDiem

#  LẤY ID ĐÃ THÍCH
def get_favorite_ids(db: Session, user_id):
    rows = (
        db.query(YeuThich.ma_dia_diem)
        .filter(YeuThich.ma_nguoi_dung == user_id)
        .all()
    )
    return [row.ma_dia_diem for row in rows]

# TOGGLE FAVORITE
def toggle_favorite(db: Session, user_id, dia_diem_id):

    existing = (
        db.query(YeuThich)
        .filter(
            YeuThich.ma_nguoi_dung == user_id,
            YeuThich.ma_dia_diem == dia_diem_id
        )
        .first()
    )

    if existing:
        db.delete(existing)
        db.commit()
        return False  

    db.add(YeuThich(
        ma_nguoi_dung=user_id,
        ma_dia_diem=dia_diem_id
    ))
    db.commit()

    return True  

# LẤY DANH SÁCH YÊU THÍCH
def get_my_favorites(db: Session, user_id):
    results = (
        db.query(DiaDiem)
        .join(YeuThich, DiaDiem.ma_dia_diem == YeuThich.ma_dia_diem)
        .filter(YeuThich.ma_nguoi_dung == user_id)
        .all()
    )

    data = []
    for item in results:
        data.append({
            "ma_dia_diem": str(item.ma_dia_diem),
            "ten": item.ten,
            "danh_gia": item.danh_gia,
            "gia_trung_binh": item.gia_trung_binh,
            "is_favorite": True 
        })

    return data