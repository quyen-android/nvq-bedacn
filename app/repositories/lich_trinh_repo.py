from app.models.lich_trinh import LichTrinh
from app.models.chuyen_di import ChuyenDi
from app.models.khung_gio_vang import KhungGioVang
from sqlalchemy.orm import joinedload

def get_by_id(db, ma_lich_trinh):
    return db.query(LichTrinh).filter(
        LichTrinh.ma_lich_trinh == ma_lich_trinh
    ).first()

def get_by_chuyen_di(db, ma_chuyen_di):
    return (
        db.query(LichTrinh)
        .options(
            joinedload(LichTrinh.chi_tiets)
        )
        .filter(LichTrinh.ma_chuyen_di == ma_chuyen_di)
        .order_by(LichTrinh.ngay.asc())
        .all()
    )


def delete_by_chuyen_di(db, ma_chuyen_di):
    lich_trinhs = (
        db.query(LichTrinh)
        .filter(LichTrinh.ma_chuyen_di == ma_chuyen_di)
        .all()
    )

    for item in lich_trinhs:
        db.delete(item)

    db.flush()
    
def get_all(db):
    return db.query(KhungGioVang).all()


def get_by_id(db, ma_khung_gio):
    return (
        db.query(KhungGioVang)
        .filter(KhungGioVang.ma_khung_gio == ma_khung_gio)
        .first()
    )


def get_by_dia_diem(db, ma_dia_diem):
    return (
        db.query(KhungGioVang)
        .filter(KhungGioVang.ma_dia_diem == ma_dia_diem)
        .order_by(
            KhungGioVang.thang_bat_dau.asc(),
            KhungGioVang.gio_bat_dau.asc()
        )
        .all()
    )


def create(db, item):
    db.add(item)
    db.flush()
    return item


def delete(db, item):
    db.delete(item)
    db.flush()