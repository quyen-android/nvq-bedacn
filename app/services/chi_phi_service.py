from app.repositories import tinh_repo, phuong_tien_repo
from app.utils.distance import haversine


def tinh_gia_ve(
    db,
    ma_tinh_di,
    ma_tinh_den,
    ma_pt
):
    tinh_di = tinh_repo.get_by_id(db, ma_tinh_di)
    tinh_den = tinh_repo.get_by_id(db, ma_tinh_den)

    phuong_tien = phuong_tien_repo.get_gia_km(
        db,
        ma_pt
    )

    khoang_cach = haversine(
        tinh_di.vi_do,
        tinh_di.kinh_do,
        tinh_den.vi_do,
        tinh_den.kinh_do
    )

    gia_ve = khoang_cach * phuong_tien.gia_km

    return {
        "khoang_cach": round(khoang_cach, 2),
        "gia_ve": round(gia_ve, 0)
    }