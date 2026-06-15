from datetime import datetime, time, timedelta
from decimal import Decimal
from uuid import UUID

from app.models.lich_trinh import LichTrinh
from app.models.chi_tiet_lich_trinh import ChiTietLichTrinh


class LuuLichTrinhAIService:

    @staticmethod
    def parse_uuid(value):
        if not value:
            return None

        try:
            return UUID(str(value))
        except Exception:
            return None

    @staticmethod
    def parse_time(value):
        if not value:
            return None

        if value == "overnight":
            return time(23, 59)

        try:
            return datetime.strptime(
                str(value),
                "%H:%M"
            ).time()
        except Exception:
            return None

    @staticmethod
    def to_float(value, default=0.0):
        if value is None:
            return default

        try:
            return float(value)
        except Exception:
            return default

    @staticmethod
    def to_decimal(value, default=0):
        if value is None:
            value = default

        try:
            return Decimal(str(value))
        except Exception:
            return Decimal(str(default))

    @staticmethod
    def get_item_distance_and_cost(item):
        khoang_cach = (
            item.get("distance_km")
            or item.get("khoang_cach")
            or item.get("khoang_cach_km")
            or 0
        )

        gia = (
            item.get("estimated_transport_cost")
            or item.get("chi_phi_di_chuyen")
            or item.get("gia")
            or 0
        )

        return khoang_cach, gia

    @classmethod
    def xoa_lich_trinh_cu(
        cls,
        db,
        ma_chuyen_di
    ):
        lich_trinhs = (
            db.query(LichTrinh)
            .filter(
                LichTrinh.ma_chuyen_di == ma_chuyen_di
            )
            .all()
        )

        for lich_trinh in lich_trinhs:
            db.delete(lich_trinh)

        db.flush()

    @classmethod
    def luu(
        cls,
        db,
        chuyen_di,
        lich_trinh_ai
    ):
        if not lich_trinh_ai:
            raise ValueError("Lịch trình AI rỗng")

        days = lich_trinh_ai.get("days", [])

        if not days:
            raise ValueError("Lịch trình AI không có days")

        cls.xoa_lich_trinh_cu(
            db,
            chuyen_di.ma_chuyen_di
        )

        lich_trinh_da_luu = []

        for day in days:
            so_ngay = int(day.get("day") or 1)

            ngay_lich_trinh = (
                chuyen_di.ngay_di
                + timedelta(days=so_ngay - 1)
            )

            lich_trinh = LichTrinh(
                ma_chuyen_di=chuyen_di.ma_chuyen_di,
                tieu_de=f"Ngày {so_ngay}",
                ngay=ngay_lich_trinh
            )

            db.add(lich_trinh)
            db.flush()

            items = day.get("items", [])

            for item in items:
                ma_dia_diem = cls.parse_uuid(
                    item.get("id")
                    or item.get("ma_dia_diem")
                )

                ma_pt = cls.parse_uuid(
                    item.get("ma_pt")
                )

                gio_bat_dau = cls.parse_time(
                    item.get("start_time")
                    or item.get("gio_bat_dau")
                )

                gio_ket_thuc = cls.parse_time(
                    item.get("end_time")
                    or item.get("gio_ket_thuc")
                )

                khoang_cach, gia = cls.get_item_distance_and_cost(
                    item
                )

                so_luong_pt = int(
                    item.get("number_of_vehicles")
                    or item.get("so_luong_pt")
                    or 1
                )

                chi_tiet = ChiTietLichTrinh(
                    ma_lich_trinh=lich_trinh.ma_lich_trinh,
                    ma_dia_diem=ma_dia_diem,
                    gio_bat_dau=gio_bat_dau,
                    gio_ket_thuc=gio_ket_thuc,
                    ma_pt=ma_pt,

                    # quan trọng
                    khoang_cach=cls.to_float(khoang_cach),
                    so_luong_pt=so_luong_pt,
                    gia=cls.to_decimal(gia)
                )

                db.add(chi_tiet)

            lich_trinh_da_luu.append(
                lich_trinh
            )

        chuyen_di.trang_thai = "ban_nhap"
        chuyen_di.ngay_cap_nhat = datetime.utcnow()

        db.commit()

        return {
            "ma_chuyen_di": str(chuyen_di.ma_chuyen_di),
            "so_ngay_da_luu": len(lich_trinh_da_luu),
            "trang_thai": chuyen_di.trang_thai
        }