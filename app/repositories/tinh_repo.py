from sqlalchemy import func
from app.models.tinh import Tinh

def get_all(db):
    return db.query(Tinh).all()


def get_by_id(db, ma_tinh):
    return (
        db.query(Tinh)
        .filter(Tinh.ma_tinh == ma_tinh)
        .first()
    )


def get_by_name_and_country(db, ten_tinh, quoc_gia):
    return (
        db.query(Tinh)
        .filter(
            func.lower(Tinh.ten_tinh) == ten_tinh.strip().lower(),
            func.lower(Tinh.quoc_gia) == quoc_gia.strip().lower()
        )
        .first()
    )


def create(db, data):
    tinh = Tinh(
        ten_tinh=data.ten_tinh.strip(),
        quoc_gia=data.quoc_gia.strip(),
        kinh_do=data.kinh_do,
        vi_do=data.vi_do
    )

    db.add(tinh)
    db.flush()

    return tinh


def update(db, tinh, data):
    if data.ten_tinh is not None:
        tinh.ten_tinh = data.ten_tinh.strip()

    if data.quoc_gia is not None:
        tinh.quoc_gia = data.quoc_gia.strip()

    if data.kinh_do is not None:
        tinh.kinh_do = data.kinh_do

    if data.vi_do is not None:
        tinh.vi_do = data.vi_do

    db.flush()

    return tinh


def delete(db, tinh):
    db.delete(tinh)
    db.flush()