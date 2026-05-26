from sqlalchemy import func
from app.models.the import The


def get_all(db):
    return db.query(The).all()


def get_by_id(db, ma_the):
    return (
        db.query(The)
        .filter(The.ma_the == ma_the)
        .first()
    )


def get_by_loai(db, ma_loai):
    return (
        db.query(The)
        .filter(The.ma_loai == ma_loai)
        .all()
    )


def get_by_name_and_loai(
    db,
    ten_the,
    ma_loai
):
    return (
        db.query(The)
        .filter(
            func.lower(The.ten_the) == ten_the.strip().lower(),
            The.ma_loai == ma_loai
        )
        .first()
    )


def create(db, data):
    the = The(
        ten_the=data.ten_the.strip(),
        ma_loai=data.ma_loai
    )

    db.add(the)
    db.flush()

    return the


def update(db, the, data):
    if data.ten_the is not None:
        the.ten_the = data.ten_the.strip()

    if data.ma_loai is not None:
        the.ma_loai = data.ma_loai

    db.flush()

    return the


def delete(db, the):
    db.delete(the)
    db.flush()