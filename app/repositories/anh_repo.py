from app.models.anh_dia_diem import AnhDiaDiem

def add_images(db, ma_dia_diem, filenames):
    for f in filenames:
        db.add(AnhDiaDiem(
            ma_dia_diem=ma_dia_diem,
            url=f
        ))
    db.commit()


def delete_images(db, ma_dia_diem):
    db.query(AnhDiaDiem).filter(
        AnhDiaDiem.ma_dia_diem == ma_dia_diem
    ).delete()
    db.commit()