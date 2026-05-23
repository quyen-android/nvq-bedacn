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