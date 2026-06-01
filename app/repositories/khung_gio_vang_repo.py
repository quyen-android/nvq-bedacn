from app.models.khung_gio_vang import KhungGioVang


def get_by_dia_diem_and_month(
    db,
    ma_dia_diem,
    month
):
    return (
        db.query(KhungGioVang)
        .filter(
            KhungGioVang.ma_dia_diem == ma_dia_diem,
            KhungGioVang.thang_bat_dau <= month,
            KhungGioVang.thang_ket_thuc >= month
        )
        .order_by(
            KhungGioVang.gio_bat_dau.asc()
        )
        .all()
    )

def get_all(db):
    return (
        db.query(KhungGioVang)
        .order_by(
            KhungGioVang.thang_bat_dau.asc(),
            KhungGioVang.gio_bat_dau.asc()
        )
        .all()
    )


def get_by_id(db, ma_khung_gio):
    return (
        db.query(KhungGioVang)
        .filter(
            KhungGioVang.ma_khung_gio == ma_khung_gio
        )
        .first()
    )


def get_by_dia_diem(db, ma_dia_diem):
    return (
        db.query(KhungGioVang)
        .filter(
            KhungGioVang.ma_dia_diem == ma_dia_diem
        )
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