from app.models.loai_dia_diem import LoaiDiaDiem

# def get_by_id(db, id):
#     return db.query(LoaiDiaDiem).filter(
#         LoaiDiaDiem.ma_dia_diem == id
#     ).first()

def get_by_id(db, ma_loai):
    return (
        db.query(LoaiDiaDiem)
        .filter(
            LoaiDiaDiem.ma_loai == ma_loai
        )
        .first()
    )