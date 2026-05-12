from app.repositories import tinh_repo, phuong_tien_repo, chuyen_di_repo,lich_trinh_repo,chi_tiet_lich_trinh_repo, dia_diem_repo, loai_dia_diem_repo
from app.utils.distance import haversine
from math import ceil

from app.utils.distance import haversine

# giá vé đi lại giá vé liên tỉnh:  (khoảng cách tỉnh đến và tỉnh đi ) * giá / km (lấy mã tỉnh từ db của chuyến đi join với bảng tỉnh để lấy kinh độ và vĩ độ rồi * với mã phương tiện chuyến đi join từ bảng phương tiện)
# giá xe địa phương: (khoảng cách giữa các điểm) * giá / km * số xe(số người chia ra bao nhiêu xe)  (địa điểm, chuyến đi, phương tiện, lịch trình, chi tiết lịch trình )
# giá trung bình = 
        # Quán ăn: giá trung bình * số người (địa điểm, chuyến đi)
        # Nơi ở: giá trung bình (giá phòng) * số phòng (địa điểm, chuyến đi)
        # Điểm tham quan: giá trung bình (giá vé)  * số người (địa điểm, chuyến đi)

def tinh_gia_di_chuyen_lien_tinh(
    db,
    ma_chuyen_di
):
    # Lấy chuyến đi
    chuyen_di = chuyen_di_repo.get_by_id(
        db,
        ma_chuyen_di
    )

    if not chuyen_di:
        raise ValueError("Không tìm thấy chuyến đi")

    # Lấy tỉnh đi và tỉnh đến
    tinh_di = tinh_repo.get_by_id(
        db,
       chuyen_di.ma_tinh_di
    )

    tinh_den = tinh_repo.get_by_id(
        db,
        chuyen_di.ma_tinh_den
    )

    if not tinh_di or not tinh_den:
        raise ValueError("Không tìm thấy tỉnh")

    # Lấy phương tiện
    phuong_tien = phuong_tien_repo.get_by_id(
        db,
        chuyen_di.ma_pt
    )

    if not phuong_tien:
        raise ValueError("Không tìm thấy phương tiện")

    # Tính khoảng cách
    khoang_cach = haversine(
        tinh_di.vi_do,
        tinh_di.kinh_do,
        tinh_den.vi_do,
        tinh_den.kinh_do
    )

    # Giá cho 1 người
    gia_1_nguoi = (
        float(khoang_cach) *
        float(phuong_tien.gia_moi_km)
    )

    # Tổng giá
    tong_gia = (
        gia_1_nguoi *
        chuyen_di.so_nguoi
    )

    return {
        "ma_chuyen_di": chuyen_di.ma_chuyen_di,
        "tinh_di": tinh_di.ten_tinh,
        "tinh_den": tinh_den.ten_tinh,
        "phuong_tien": phuong_tien.ten_pt,
        "so_nguoi": chuyen_di.so_nguoi,
        "khoang_cach_km": round(khoang_cach, 2),
        "gia_moi_km": phuong_tien.gia_moi_km,
        "gia_1_nguoi": round(gia_1_nguoi, 0),
        "tong_gia": round(tong_gia, 0)
    }

def tinh_chi_phi_di_chuyen_dia_phuong(
    db,
    ma_chuyen_di,
    ma_lich_trinh
):
    # lấy chuyến đi
    chuyen_di = (
        chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )
    )

    if not chuyen_di:
        raise ValueError(
            "Không tìm thấy chuyến đi"
        )

    so_nguoi = chuyen_di.so_nguoi

    # lấy danh sách chi tiết lịch trình
    chi_tiets = (
        chi_tiet_lich_trinh_repo
        .get_by_lich_trinh(
            db,
            ma_lich_trinh
        )
    )

    if not chi_tiets:
        raise ValueError(
            "Không có chi tiết lịch trình"
        )

    # sắp xếp theo thời gian
    chi_tiets = sorted(
        chi_tiets,
        key=lambda x: x.gio_bat_dau
    )

    tong_khoang_cach = 0
    tong_chi_phi = 0

    # duyệt từng cặp địa điểm liên tiếp
    for i in range(len(chi_tiets) - 1):

        ct_hien_tai = chi_tiets[i]
        ct_ke_tiep = chi_tiets[i + 1]

        diem_1 = ct_hien_tai.dia_diem
        diem_2 = ct_ke_tiep.dia_diem

        # bỏ qua nếu thiếu địa điểm
        if not diem_1 or not diem_2:
            continue

        # phương tiện dùng để đi tới điểm tiếp theo
        ma_pt = ct_ke_tiep.ma_pt

        if not ma_pt:
            continue

        phuong_tien = (
            phuong_tien_repo.get_by_id(
                db,
                ma_pt
            )
        )

        if not phuong_tien:
            continue

        # tính khoảng cách
        khoang_cach = haversine(
            diem_1.vi_do,
            diem_1.kinh_do,
            diem_2.vi_do,
            diem_2.kinh_do
        )

        # giá mỗi km
        gia_km = float(
            phuong_tien.gia_moi_km
        )

        # sức chứa
        suc_chua = (
            phuong_tien.suc_chua
        )

        # số lượng xe đề xuất
        so_luong_pt = ceil(
            so_nguoi / suc_chua
        )

        # tính giá
        gia = (
            khoang_cach *
            gia_km *
            so_luong_pt
        )

        # cập nhật DB
        chi_tiet_lich_trinh_repo.update_chi_phi(
            db=db,
            chi_tiet=ct_ke_tiep,
            khoang_cach=round(
                khoang_cach,
                2
            ),
            so_luong_pt=so_luong_pt,
            gia=round(
                gia,
                2
            )
        )

        tong_khoang_cach += khoang_cach
        tong_chi_phi += gia

    db.commit()

    return {
        "tong_khoang_cach": round(
            tong_khoang_cach,
            2
        ),

        "tong_chi_phi": round(
            tong_chi_phi,
            2
        )
    }

def tinh_tong_chi_phi_di_chuyen(
    db,
    ma_chuyen_di
):
    # lấy danh sách lịch trình
    lich_trinhs = (
        lich_trinh_repo.get_by_chuyen_di(
            db,
            ma_chuyen_di
        )
    )

    # chi phí liên tỉnh
    chi_phi_lien_tinh = (
        tinh_gia_di_chuyen_lien_tinh(
            db,
            ma_chuyen_di
        )
    )

    tong_chi_phi_dia_phuong = 0
    tong_khoang_cach = 0

    # duyệt từng lịch trình
    for lich_trinh in lich_trinhs:

        result = (
            tinh_chi_phi_di_chuyen_dia_phuong(
                db=db,
                ma_chuyen_di=ma_chuyen_di,
                ma_lich_trinh=(
                    lich_trinh.ma_lich_trinh
                )
            )
        )

        tong_chi_phi_dia_phuong += (
            result["tong_chi_phi"]
        )

        tong_khoang_cach += (
            result["tong_khoang_cach"]
        )

    tong_chi_phi = (
        chi_phi_lien_tinh["tong_gia"] +
        tong_chi_phi_dia_phuong
    )

    return {
        "chi_phi_lien_tinh": round(
            chi_phi_lien_tinh["tong_gia"],
            0
        ),

        "chi_phi_dia_phuong": round(
            tong_chi_phi_dia_phuong,
            0
        ),

        "tong_khoang_cach": round(
            tong_khoang_cach,
            2
        ),

        "tong_chi_phi_di_chuyen": round(
            tong_chi_phi,
            0
        )
    }

def tinh_chi_phi_an_uong(
    db,
    ma_chuyen_di
):
    chuyen_di = (
        chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )
    )

    if not chuyen_di:
        raise ValueError(
            "Không tìm thấy chuyến đi"
        )

    so_nguoi = chuyen_di.so_nguoi

    tong_chi_phi = 0

    lich_trinhs = (
        lich_trinh_repo.get_by_chuyen_di(
            db,
            ma_chuyen_di
        )
    )

    for lich_trinh in lich_trinhs:

        chi_tiets = (
            chi_tiet_lich_trinh_repo
            .get_by_lich_trinh(
                db,
                lich_trinh.ma_lich_trinh
            )
        )

        for ct in chi_tiets:

            dia_diem = (
                dia_diem_repo.get_by_id(
                    db,
                    ct.ma_dia_diem
                )
            )

            if not dia_diem:
                continue

            loai_dia_diem = (
                loai_dia_diem_repo.get_by_id(
                    db,
                    dia_diem.ma_loai
                )
            )

            if not loai_dia_diem:
                continue

            # quán ăn
            if (
                loai_dia_diem.ten_loai
                == "Quán ăn"
            ):

                gia_tb = (
                    dia_diem.gia_trung_binh or 0
                )

                tong_chi_phi += (
                    gia_tb * so_nguoi
                )

    return {
        "tong_chi_phi_an_uong": round(
            tong_chi_phi,
            0
        )
    }

def tinh_chi_phi_tham_quan(
    db,
    ma_chuyen_di
):
    chuyen_di = (
        chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )
    )

    if not chuyen_di:
        raise ValueError(
            "Không tìm thấy chuyến đi"
        )

    so_nguoi = chuyen_di.so_nguoi

    tong_chi_phi = 0

    lich_trinhs = (
        lich_trinh_repo.get_by_chuyen_di(
            db,
            ma_chuyen_di
        )
    )

    for lich_trinh in lich_trinhs:

        chi_tiets = (
            chi_tiet_lich_trinh_repo
            .get_by_lich_trinh(
                db,
                lich_trinh.ma_lich_trinh
            )
        )

        for ct in chi_tiets:

            dia_diem = (
                dia_diem_repo.get_by_id(
                    db,
                    ct.ma_dia_diem
                )
            )

            if not dia_diem:
                continue

            loai_dia_diem = (
                loai_dia_diem_repo.get_by_id(
                    db,
                    dia_diem.ma_loai
                )
            )

            if not loai_dia_diem:
                continue

            # tham quan
            if (
                loai_dia_diem.ten_loai
                == "Điểm tham quan"
            ):

                gia_ve = (
                    dia_diem.gia_trung_binh or 0
                )

                chi_phi = (
                    gia_ve * so_nguoi
                )

                # update DB
                ct.chi_phi_tham_quan = (
                    round(chi_phi, 2)
                )

                tong_chi_phi += chi_phi

    db.commit()

    return {
        "tong_chi_phi_tham_quan": round(
            tong_chi_phi,
            0
        )
    }

from math import ceil


def tinh_chi_phi_luu_tru(
    db,
    ma_chuyen_di
):
    chuyen_di = (
        chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )
    )

    if not chuyen_di:
        raise ValueError(
            "Không tìm thấy chuyến đi"
        )

    so_nguoi = chuyen_di.so_nguoi

    tong_chi_phi = 0

    lich_trinhs = (
        lich_trinh_repo.get_by_chuyen_di(
            db,
            ma_chuyen_di
        )
    )

    for lich_trinh in lich_trinhs:

        chi_tiets = (
            chi_tiet_lich_trinh_repo
            .get_by_lich_trinh(
                db,
                lich_trinh.ma_lich_trinh
            )
        )

        for ct in chi_tiets:

            dia_diem = (
                dia_diem_repo.get_by_id(
                    db,
                    ct.ma_dia_diem
                )
            )

            if not dia_diem:
                continue

            loai_dia_diem = (
                loai_dia_diem_repo.get_by_id(
                    db,
                    dia_diem.ma_loai
                )
            )

            if not loai_dia_diem:
                continue

            # lưu trú
            if (
                loai_dia_diem.ten_loai == "Chỗ ở"
            ):

                gia_phong = (
                    dia_diem.gia_trung_binh or 0
                )

                suc_chua = 3

                so_phong = ceil(
                    so_nguoi / suc_chua
                )

                chi_phi = (
                    gia_phong * so_phong
                )

                # update DB
                ct.chi_phi_luu_tru = (
                    round(chi_phi, 2)
                )

                tong_chi_phi += chi_phi

    db.commit()

    return {
        "tong_chi_phi_luu_tru": round(
            tong_chi_phi,
            0
        )
    }

def tinh_tong_chi_phi_chuyen_di(
    db,
    ma_chuyen_di,
    so_phong=1
):
    # =========================
    # DI CHUYỂN
    # =========================
    chi_phi_di_chuyen = (
        tinh_tong_chi_phi_di_chuyen(
            db,
            ma_chuyen_di
        )
    )

    # =========================
    # ĂN UỐNG
    # =========================
    chi_phi_an_uong = (
        tinh_chi_phi_an_uong(
            db,
            ma_chuyen_di
        )
    )

    # =========================
    # LƯU TRÚ
    # =========================
    chi_phi_luu_tru = (
        tinh_chi_phi_luu_tru(
            db,
            ma_chuyen_di,
            so_phong
        )
    )

    # =========================
    # THAM QUAN
    # =========================
    chi_phi_tham_quan = (
        tinh_chi_phi_tham_quan(
            db,
            ma_chuyen_di
        )
    )

    # =========================
    # TỔNG CHI PHÍ
    # =========================
    tong_chi_phi = (
        chi_phi_di_chuyen["tong_chi_phi_di_chuyen"]
        +
        chi_phi_an_uong["tong_chi_phi_an_uong"]
        +
        chi_phi_luu_tru["tong_chi_phi_luu_tru"]
        +
        chi_phi_tham_quan["tong_chi_phi_tham_quan"]
    )

    # =========================
    # LẤY NGÂN SÁCH
    # =========================
    chuyen_di = (
        chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )
    )

    ngan_sach = (
        chuyen_di.ngan_sach or 0
    )

    vuot_ngan_sach = (
        tong_chi_phi > ngan_sach
    )

    so_tien_vuot = max(
        tong_chi_phi - ngan_sach,
        0
    )

    so_tien_con_lai = max(
        ngan_sach - tong_chi_phi,
        0
    )

    return {
        "chi_phi_di_chuyen": (
            chi_phi_di_chuyen[
                "tong_chi_phi_di_chuyen"
            ]
        ),

        "chi_phi_an_uong": (
            chi_phi_an_uong[
                "tong_chi_phi_an_uong"
            ]
        ),

        "chi_phi_luu_tru": (
            chi_phi_luu_tru[
                "tong_chi_phi_luu_tru"
            ]
        ),

        "chi_phi_tham_quan": (
            chi_phi_tham_quan[
                "tong_chi_phi_tham_quan"
            ]
        ),

        "tong_chi_phi": round(
            tong_chi_phi,
            0
        ),

        "ngan_sach": ngan_sach,

        "vuot_ngan_sach": (
            vuot_ngan_sach
        ),

        "so_tien_vuot": round(
            so_tien_vuot,
            0
        ),

        "so_tien_con_lai": round(
            so_tien_con_lai,
            0
        )
    }