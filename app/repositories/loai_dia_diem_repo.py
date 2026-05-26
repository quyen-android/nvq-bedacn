from sqlalchemy import func
from app.models.loai_dia_diem import LoaiDiaDiem


def get_all(db):
    return db.query(LoaiDiaDiem).all()


def get_by_id(db, ma_loai):
    return (
        db.query(LoaiDiaDiem)
        .filter(LoaiDiaDiem.ma_loai == ma_loai)
        .first()
    )


def get_by_name(db, ten_loai):
    return (
        db.query(LoaiDiaDiem)
        .filter(
            func.lower(LoaiDiaDiem.ten_loai)
            == ten_loai.strip().lower()
        )
        .first()
    )


def create(db, data):
    loai = LoaiDiaDiem(
        ten_loai=data.ten_loai.strip()
    )

    db.add(loai)
    db.flush()

    return loai


def update(db, loai, data):
    if data.ten_loai is not None:
        loai.ten_loai = data.ten_loai.strip()

    db.flush()

    return loai


def delete(db, loai):
    db.delete(loai)
    db.flush()