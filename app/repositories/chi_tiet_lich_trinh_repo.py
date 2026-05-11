from app.models.chi_tiet_lich_trinh import ChiTietLichTrinh

def get_by_lich_trinh(db, ma_lich_trinh):
    return db.query(ChiTietLichTrinh).filter(
        ChiTietLichTrinh.ma_lich_trinh == ma_lich_trinh
    ).all()

def get_by_id(db, ma_ct):
    return db.query(ChiTietLichTrinh).filter(
        ChiTietLichTrinh.ma_ct == ma_ct
    ).first()

def update_so_luong_pt(
    db,
    chi_tiet,
    so_luong_pt,
    gia
):
    chi_tiet.so_luong_pt = (
        so_luong_pt
    )

    chi_tiet.gia = gia

    db.commit()
    db.refresh(chi_tiet)

    return chi_tiet

def update_chi_phi(
    db,
    chi_tiet,
    khoang_cach,
    so_luong_pt,
    gia
):
    chi_tiet.khoang_cach = (
        khoang_cach
    )

    chi_tiet.so_luong_pt = (
        so_luong_pt
    )

    chi_tiet.gia = gia

    db.add(chi_tiet)