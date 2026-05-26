from sqlalchemy import func
from app.models.so_thich_am_thuc import SoThichAmThuc


def get_all(db):
    return db.query(SoThichAmThuc).all()


def get_by_id(db, ma_so_thich):
    return (
        db.query(SoThichAmThuc)
        .filter(SoThichAmThuc.ma_so_thich == ma_so_thich)
        .first()
    )


def get_by_name(db, ten_so_thich):
    return (
        db.query(SoThichAmThuc)
        .filter(
            func.lower(SoThichAmThuc.ten_so_thich)
            == ten_so_thich.strip().lower()
        )
        .first()
    )


def create(db, data):
    item = SoThichAmThuc(
        ten_so_thich=data.ten_so_thich.strip()
    )

    db.add(item)
    db.flush()

    return item


def update(db, item, data):
    if data.ten_so_thich is not None:
        item.ten_so_thich = data.ten_so_thich.strip()

    db.flush()

    return item


def delete(db, item):
    db.delete(item)
    db.flush()