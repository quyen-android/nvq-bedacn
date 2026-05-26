from sqlalchemy import func
from app.models.loai_du_lich import LoaiDuLich


def get_all(db):
    return db.query(LoaiDuLich).all()


def get_by_id(db, ma_loai_du_lich):
    return (
        db.query(LoaiDuLich)
        .filter(LoaiDuLich.ma_loai_du_lich == ma_loai_du_lich)
        .first()
    )


def get_by_name(db, ten_loai):
    return (
        db.query(LoaiDuLich)
        .filter(
            func.lower(LoaiDuLich.ten_loai)
            == ten_loai.strip().lower()
        )
        .first()
    )


def create(db, data):
    item = LoaiDuLich(
        ten_loai=data.ten_loai.strip()
    )

    db.add(item)
    db.flush()

    return item


def update(db, item, data):
    if data.ten_loai is not None:
        item.ten_loai = data.ten_loai.strip()

    db.flush()

    return item


def delete(db, item):
    db.delete(item)
    db.flush()