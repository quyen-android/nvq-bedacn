from app.repositories import chi_tiet_lich_trinh_repo, phuong_tien_repo

def update_so_luong_pt(
    db,
    ma_ct,
    so_luong_pt
):
    chi_tiet = (
        chi_tiet_lich_trinh_repo
        .get_by_id(
            db,
            ma_ct
        )
    )

    if not chi_tiet:
        raise ValueError(
            "Không tìm thấy chi tiết"
        )

    phuong_tien = (
        phuong_tien_repo
        .get_by_id(
            db,
            chi_tiet.ma_pt
        )
    )

    gia_km = float(
        phuong_tien.gia_moi_km
    )

    gia = round(
        chi_tiet.khoang_cach *
        gia_km *
        so_luong_pt,
        2
    )

    return (
        chi_tiet_lich_trinh_repo
        .update_so_luong_pt(
            db,
            chi_tiet,
            so_luong_pt,
            gia
        )
    )