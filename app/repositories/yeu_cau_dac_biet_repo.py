from sqlalchemy import func
from app.models.yeu_cau_dac_biet import YeuCauDacBiet


def get_all(db):
    return db.query(YeuCauDacBiet).all()


def get_by_id(db, ma_yeu_cau):
    return (
        db.query(YeuCauDacBiet)
        .filter(YeuCauDacBiet.ma_yeu_cau == ma_yeu_cau)
        .first()
    )


def get_by_name(db, ten_yeu_cau):
    return (
        db.query(YeuCauDacBiet)
        .filter(
            func.lower(YeuCauDacBiet.ten_yeu_cau)
            == ten_yeu_cau.strip().lower()
        )
        .first()
    )


def create(db, data):
    item = YeuCauDacBiet(
        ten_yeu_cau=data.ten_yeu_cau.strip()
    )

    db.add(item)
    db.flush()

    return item


def update(db, item, data):
    if data.ten_yeu_cau is not None:
        item.ten_yeu_cau = data.ten_yeu_cau.strip()

    db.flush()

    return item


def delete(db, item):
    db.delete(item)
    db.flush()