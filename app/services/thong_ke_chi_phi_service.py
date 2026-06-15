import math

from app.models.chuyen_di import ChuyenDi
from app.models.lich_trinh import LichTrinh
from app.models.chi_tiet_lich_trinh import ChiTietLichTrinh
from app.models.dia_diem import DiaDiem
from app.models.phuong_tien import PhuongTien

from app.utils.distance import haversine


class ThongKeChiPhiService:

    @staticmethod
    def to_float(value, default=0):
        try:
            return float(value or default)
        except Exception:
            return float(default)

    @staticmethod
    def check_owner(db, ma_chuyen_di, current_user):
        chuyen_di = (
            db.query(ChuyenDi)
            .filter(
                ChuyenDi.ma_chuyen_di == ma_chuyen_di,
                ChuyenDi.ma_nguoi_dung == current_user.ma_nguoi_dung
            )
            .first()
        )

        if not chuyen_di:
            raise ValueError("Không tìm thấy chuyến đi")

        return chuyen_di

    @classmethod
    def is_accommodation(cls, dia_diem):
        if not dia_diem or not dia_diem.loai:
            return False

        ten_loai = str(dia_diem.loai.ten_loai or "").lower()

        return "chỗ ở" in ten_loai or "khách sạn" in ten_loai

    @classmethod
    def get_place_cost(cls, dia_diem, so_nguoi):
        if not dia_diem:
            return 0

        gia = cls.to_float(dia_diem.gia_trung_binh)
        so_nguoi = int(so_nguoi or 1)

        if cls.is_accommodation(dia_diem):
            so_phong = math.ceil(so_nguoi / 2)
            return gia * so_phong

        return gia * so_nguoi

    @classmethod
    def get_phuong_tien_lien_tinh(cls, db, chuyen_di):
        ma_pt_di = getattr(chuyen_di, "ma_pt_di", None)
        ma_pt_ve = getattr(chuyen_di, "ma_pt_ve", None)

        if not ma_pt_di:
            ma_pt_di = getattr(chuyen_di, "ma_pt", None)

        if not ma_pt_ve:
            ma_pt_ve = ma_pt_di

        if not ma_pt_di:
            return None, None

        pt_di = (
            db.query(PhuongTien)
            .filter(PhuongTien.ma_pt == ma_pt_di)
            .first()
        )

        pt_ve = (
            db.query(PhuongTien)
            .filter(PhuongTien.ma_pt == ma_pt_ve)
            .first()
        )

        return pt_di, pt_ve

    @classmethod
    def tinh_chi_phi_lien_tinh(cls, db, chuyen_di, so_nguoi):
        tinh_di = chuyen_di.tinh_di
        tinh_den = chuyen_di.tinh_den

        if not tinh_di or not tinh_den:
            return {
                "khoang_cach_km": 0,
                "luot_di": None,
                "luot_ve": None,
                "tong_chi_phi_lien_tinh": 0
            }

        if (
            tinh_di.vi_do is None
            or tinh_di.kinh_do is None
            or tinh_den.vi_do is None
            or tinh_den.kinh_do is None
        ):
            return {
                "khoang_cach_km": 0,
                "luot_di": None,
                "luot_ve": None,
                "tong_chi_phi_lien_tinh": 0
            }

        pt_di, pt_ve = cls.get_phuong_tien_lien_tinh(
            db=db,
            chuyen_di=chuyen_di
        )

        if not pt_di or not pt_ve:
            return {
                "khoang_cach_km": 0,
                "luot_di": None,
                "luot_ve": None,
                "tong_chi_phi_lien_tinh": 0
            }

        khoang_cach_km = haversine(
            float(tinh_di.vi_do),
            float(tinh_di.kinh_do),
            float(tinh_den.vi_do),
            float(tinh_den.kinh_do)
        )

        chi_phi_di = (
            float(khoang_cach_km)
            * cls.to_float(pt_di.gia_moi_km)
            * int(so_nguoi or 1)
        )

        chi_phi_ve = (
            float(khoang_cach_km)
            * cls.to_float(pt_ve.gia_moi_km)
            * int(so_nguoi or 1)
        )

        return {
            "khoang_cach_km": round(khoang_cach_km, 2),
            "luot_di": {
                "ma_pt": str(pt_di.ma_pt),
                "ten_pt": pt_di.ten_pt,
                "chi_phi": round(chi_phi_di, 0)
            },
            "luot_ve": {
                "ma_pt": str(pt_ve.ma_pt),
                "ten_pt": pt_ve.ten_pt,
                "chi_phi": round(chi_phi_ve, 0)
            },
            "tong_chi_phi_lien_tinh": round(chi_phi_di + chi_phi_ve, 0)
        }

    @classmethod
    def thong_ke_theo_chuyen_di(cls, db, ma_chuyen_di, current_user):
        chuyen_di = cls.check_owner(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

        so_nguoi = int(chuyen_di.so_nguoi or 1)
        ngan_sach = cls.to_float(chuyen_di.ngan_sach)

        chi_phi_lien_tinh_info = cls.tinh_chi_phi_lien_tinh(
            db=db,
            chuyen_di=chuyen_di,
            so_nguoi=so_nguoi
        )

        chi_phi_lien_tinh = cls.to_float(
            chi_phi_lien_tinh_info.get("tong_chi_phi_lien_tinh")
        )

        lich_trinhs = (
            db.query(LichTrinh)
            .filter(LichTrinh.ma_chuyen_di == ma_chuyen_di)
            .order_by(LichTrinh.ngay.asc())
            .all()
        )

        chi_phi_an_uong = 0
        chi_phi_tham_quan = 0
        chi_phi_luu_tru = 0
        chi_phi_di_chuyen_noi_tinh = 0
        chi_phi_khac = 0

        days = []

        for index, lich_trinh in enumerate(lich_trinhs, start=1):
            chi_tiets = (
                db.query(ChiTietLichTrinh)
                .filter(
                    ChiTietLichTrinh.ma_lich_trinh
                    == lich_trinh.ma_lich_trinh
                )
                .all()
            )

            day_place_cost = 0
            day_transport_cost = 0
            day_food_cost = 0
            day_attraction_cost = 0
            day_accommodation_cost = 0
            day_other_cost = 0

            for ct in chi_tiets:
                transport_cost = cls.to_float(ct.gia)
                day_transport_cost += transport_cost

                dia_diem = None

                if ct.ma_dia_diem:
                    dia_diem = (
                        db.query(DiaDiem)
                        .filter(DiaDiem.ma_dia_diem == ct.ma_dia_diem)
                        .first()
                    )

                if not dia_diem:
                    continue

                place_cost = cls.get_place_cost(
                    dia_diem=dia_diem,
                    so_nguoi=so_nguoi
                )

                day_place_cost += place_cost

                ten_loai = ""

                if dia_diem.loai:
                    ten_loai = str(dia_diem.loai.ten_loai or "").lower()

                if "quán ăn" in ten_loai or "ăn uống" in ten_loai:
                    chi_phi_an_uong += place_cost
                    day_food_cost += place_cost
                elif "chỗ ở" in ten_loai or "khách sạn" in ten_loai:
                    chi_phi_luu_tru += place_cost
                    day_accommodation_cost += place_cost
                elif "điểm tham quan" in ten_loai or "tham quan" in ten_loai:
                    chi_phi_tham_quan += place_cost
                    day_attraction_cost += place_cost
                else:
                    chi_phi_khac += place_cost
                    day_other_cost += place_cost

            chi_phi_di_chuyen_noi_tinh += day_transport_cost

            days.append({
                "day": index,
                "ngay": str(lich_trinh.ngay),
                "chi_phi_an_uong": day_food_cost,
                "chi_phi_tham_quan": day_attraction_cost,
                "chi_phi_luu_tru": day_accommodation_cost,
                "chi_phi_khac": day_other_cost,
                "chi_phi_dia_diem": day_place_cost,
                "chi_phi_di_chuyen": day_transport_cost,
                "tong_chi_phi_ngay": day_place_cost + day_transport_cost
            })

        tong_chi_phi_noi_tinh = (
            chi_phi_an_uong
            + chi_phi_tham_quan
            + chi_phi_luu_tru
            + chi_phi_di_chuyen_noi_tinh
            + chi_phi_khac
        )

        tong_chi_phi = tong_chi_phi_noi_tinh + chi_phi_lien_tinh

        vuot_ngan_sach = tong_chi_phi > ngan_sach
        so_tien_vuot = max(tong_chi_phi - ngan_sach, 0)
        so_tien_con_lai = max(ngan_sach - tong_chi_phi, 0)

        return {
            "ma_chuyen_di": str(chuyen_di.ma_chuyen_di),
            "ten_chuyen_di": chuyen_di.ten_chuyen_di,
            "so_nguoi": so_nguoi,
            "ngan_sach": ngan_sach,

            "chi_phi_an_uong": chi_phi_an_uong,
            "chi_phi_tham_quan": chi_phi_tham_quan,
            "chi_phi_luu_tru": chi_phi_luu_tru,

            "chi_phi_di_chuyen_noi_tinh": chi_phi_di_chuyen_noi_tinh,
            "chi_phi_lien_tinh": chi_phi_lien_tinh,
            "chi_phi_di_chuyen": (
                chi_phi_di_chuyen_noi_tinh
                + chi_phi_lien_tinh
            ),

            "chi_phi_khac": chi_phi_khac,

            "tong_chi_phi_noi_tinh": tong_chi_phi_noi_tinh,
            "tong_chi_phi": tong_chi_phi,

            "vuot_ngan_sach": vuot_ngan_sach,
            "so_tien_vuot": so_tien_vuot,
            "so_tien_con_lai": so_tien_con_lai,

            "chi_phi_lien_tinh_info": chi_phi_lien_tinh_info,
            "days": days
        }