import math

from datetime import datetime, timedelta
from decimal import Decimal

from app.models.chuyen_di import ChuyenDi
from app.models.lich_trinh import LichTrinh
from app.models.chi_tiet_lich_trinh import ChiTietLichTrinh
from app.models.dia_diem import DiaDiem
from app.models.phuong_tien import PhuongTien

from app.services.khoang_cach_service import KhoangCachService
from app.services.thong_ke_chi_phi_service import ThongKeChiPhiService


class LichTrinhService:

    @staticmethod
    def parse_time(value):
        if not value:
            return None

        if value == "overnight":
            return datetime.strptime("23:59", "%H:%M").time()

        try:
            return datetime.strptime(
                str(value),
                "%H:%M"
            ).time()
        except Exception:
            return None

    @staticmethod
    def to_uuid_string(value):
        return str(value) if value else None

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

    @staticmethod
    def get_chi_tiet_id(ct):
        value = (
            getattr(ct, "ma_chi_tiet", None)
            or getattr(ct, "ma_chi_tiet_lich_trinh", None)
            or getattr(ct, "ma_ctlt", None)
            or getattr(ct, "id", None)
        )

        return str(value) if value else None

    @classmethod
    def is_accommodation(cls, dia_diem):
        if not dia_diem or not dia_diem.loai:
            return False

        ten_loai = str(dia_diem.loai.ten_loai or "").lower()

        return (
            "chỗ ở" in ten_loai
            or "khách sạn" in ten_loai
            or "lưu trú" in ten_loai
        )

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
    def get_place_by_id(cls, db, ma_dia_diem):
        if not ma_dia_diem:
            return None

        return (
            db.query(DiaDiem)
            .filter(DiaDiem.ma_dia_diem == ma_dia_diem)
            .first()
        )

    @classmethod
    def get_vehicle_by_id(cls, db, ma_pt):
        if not ma_pt:
            return None

        return (
            db.query(PhuongTien)
            .filter(PhuongTien.ma_pt == ma_pt)
            .first()
        )

    @classmethod
    def recalculate_distance_for_days(cls, db, data):
        for day in data.days:
            previous_place = None

            for item in day.items:
                current_place = cls.get_place_by_id(
                    db=db,
                    ma_dia_diem=item.ma_dia_diem
                )

                if previous_place and current_place:
                    distance = KhoangCachService.distance_between_places(
                        previous_place,
                        current_place
                    )

                    item.distance_km = round(
                        float(distance or 0),
                        2
                    )
                else:
                    item.distance_km = 0

                if current_place:
                    previous_place = current_place

        return data

    @classmethod
    def recalculate_transport_cost_for_days(cls, db, data):
        for day in data.days:
            for item in day.items:
                vehicle = cls.get_vehicle_by_id(
                    db=db,
                    ma_pt=item.ma_pt
                )

                if not vehicle:
                    item.estimated_transport_cost = 0
                    continue

                distance = cls.to_float(item.distance_km)
                gia_moi_km = cls.to_float(vehicle.gia_moi_km)
                so_xe = int(item.number_of_vehicles or 1)

                item.estimated_transport_cost = round(
                    distance * gia_moi_km * so_xe,
                    0
                )

        return data

    @classmethod
    def get_by_chuyen_di(
        cls,
        db,
        ma_chuyen_di,
        current_user
    ):
        chuyen_di = cls.check_owner(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

        so_nguoi = chuyen_di.so_nguoi or 1

        chi_phi_lien_tinh_info = (
            ThongKeChiPhiService.tinh_chi_phi_lien_tinh(
                db=db,
                chuyen_di=chuyen_di,
                so_nguoi=so_nguoi
            )
        )

        chi_phi_lien_tinh = cls.to_float(
            chi_phi_lien_tinh_info.get(
                "tong_chi_phi_lien_tinh"
            )
        )

        lich_trinhs = (
            db.query(LichTrinh)
            .filter(LichTrinh.ma_chuyen_di == ma_chuyen_di)
            .order_by(LichTrinh.ngay.asc())
            .all()
        )

        days = []

        for index, lich_trinh in enumerate(lich_trinhs, start=1):
            chi_tiets = (
                db.query(ChiTietLichTrinh)
                .filter(
                    ChiTietLichTrinh.ma_lich_trinh
                    == lich_trinh.ma_lich_trinh
                )
                .order_by(ChiTietLichTrinh.gio_bat_dau.asc())
                .all()
            )

            items = []
            estimated_day_cost = 0
            estimated_day_item_cost = 0
            estimated_day_transport_cost = 0

            for ct in chi_tiets:
                dia_diem = cls.get_place_by_id(
                    db=db,
                    ma_dia_diem=ct.ma_dia_diem
                )

                phuong_tien = cls.get_vehicle_by_id(
                    db=db,
                    ma_pt=ct.ma_pt
                )

                start_time = (
                    ct.gio_bat_dau.strftime("%H:%M")
                    if ct.gio_bat_dau else None
                )

                end_time = (
                    ct.gio_ket_thuc.strftime("%H:%M")
                    if ct.gio_ket_thuc else None
                )

                if end_time == "23:59" and cls.is_accommodation(dia_diem):
                    end_time = "overnight"

                item_cost = cls.get_place_cost(
                    dia_diem=dia_diem,
                    so_nguoi=so_nguoi
                )

                transport_cost = cls.to_float(ct.gia)
                total_cost_to_item = item_cost + transport_cost

                estimated_day_item_cost += item_cost
                estimated_day_transport_cost += transport_cost
                estimated_day_cost += total_cost_to_item

                place_type = (
                    dia_diem.loai.ten_loai
                    if dia_diem and dia_diem.loai
                    else None
                )

                items.append({
                    "ma_chi_tiet": cls.get_chi_tiet_id(ct),

                    "ma_dia_diem": cls.to_uuid_string(ct.ma_dia_diem),
                    "id": cls.to_uuid_string(ct.ma_dia_diem),

                    "place_name": dia_diem.ten if dia_diem else None,

                    "type": (
                        "accommodation"
                        if cls.is_accommodation(dia_diem)
                        else "place"
                    ),
                    "place_type": place_type,

                    "gio_bat_dau": start_time,
                    "gio_ket_thuc": end_time,
                    "start_time": start_time,
                    "end_time": end_time,

                    "ma_pt": cls.to_uuid_string(ct.ma_pt),
                    "transport_name": (
                        phuong_tien.ten_pt
                        if phuong_tien
                        else None
                    ),
                    "suggested_transport_name": (
                        phuong_tien.ten_pt
                        if phuong_tien
                        else None
                    ),

                    "khoang_cach": cls.to_float(ct.khoang_cach),
                    "distance_km": cls.to_float(ct.khoang_cach),

                    "so_luong_pt": ct.so_luong_pt or 1,
                    "number_of_vehicles": ct.so_luong_pt or 1,

                    "estimated_item_cost": item_cost,
                    "chi_phi_dia_diem": item_cost,

                    "gia": transport_cost,
                    "estimated_transport_cost": transport_cost,
                    "chi_phi_di_chuyen": transport_cost,

                    "estimated_cost": total_cost_to_item,
                    "estimated_total_cost_to_item": total_cost_to_item,
                })

            days.append({
                "ma_lich_trinh": cls.to_uuid_string(
                    lich_trinh.ma_lich_trinh
                ),
                "day": index,
                "ngay": str(lich_trinh.ngay),
                "tieu_de": lich_trinh.tieu_de,

                "items": items,

                "estimated_day_cost": estimated_day_cost,
                "estimated_item_cost": estimated_day_item_cost,
                "estimated_transport_cost": estimated_day_transport_cost,

                "chi_phi_dia_diem": estimated_day_item_cost,
                "chi_phi_di_chuyen": estimated_day_transport_cost,
                "tong_chi_phi_ngay": estimated_day_cost
            })

        tong_chi_phi_noi_tinh = sum(
            cls.to_float(day.get("estimated_day_cost"))
            for day in days
        )

        tong_chi_phi = (
            tong_chi_phi_noi_tinh
            + chi_phi_lien_tinh
        )

        ngan_sach = cls.to_float(chuyen_di.ngan_sach)

        tong_chi_phi_noi_tinh = sum(
            cls.to_float(day.get("estimated_day_cost"))
            for day in days
        )

        chi_phi_di_chuyen_noi_tinh = sum(
            cls.to_float(day.get("estimated_transport_cost"))
            for day in days
        )

        chi_phi_di_chuyen = (
            chi_phi_di_chuyen_noi_tinh
            + chi_phi_lien_tinh
        )

        tong_chi_phi = (
            tong_chi_phi_noi_tinh
            + chi_phi_lien_tinh
        )

        ngan_sach = cls.to_float(chuyen_di.ngan_sach)

        return {
            "ma_chuyen_di": cls.to_uuid_string(chuyen_di.ma_chuyen_di),
            "ten_chuyen_di": chuyen_di.ten_chuyen_di,
            "so_nguoi": so_nguoi,
            "ngan_sach": ngan_sach,

            "chi_phi_lien_tinh": chi_phi_lien_tinh,
            "chi_phi_lien_tinh_info": chi_phi_lien_tinh_info,

            "chi_phi_di_chuyen_noi_tinh": chi_phi_di_chuyen_noi_tinh,
            "chi_phi_di_chuyen_local": chi_phi_di_chuyen_noi_tinh,
            "chi_phi_di_chuyen_lien_tinh": chi_phi_lien_tinh,
            "chi_phi_di_chuyen": chi_phi_di_chuyen,

            "tong_chi_phi_noi_tinh": tong_chi_phi_noi_tinh,
            "tong_chi_phi": tong_chi_phi,

            "estimated_local_transport_cost": chi_phi_di_chuyen_noi_tinh,
            "estimated_intercity_transport_cost": chi_phi_lien_tinh,
            "estimated_transport_cost": chi_phi_di_chuyen,

            "estimated_local_cost": tong_chi_phi_noi_tinh,
            "estimated_intercity_cost": chi_phi_lien_tinh,
            "estimated_total_cost": tong_chi_phi,

            "vuot_ngan_sach": tong_chi_phi > ngan_sach,
            "so_tien_vuot": max(tong_chi_phi - ngan_sach, 0),
            "so_tien_con_lai": max(ngan_sach - tong_chi_phi, 0),

            "days": days
        }

    @classmethod
    def update_by_chuyen_di(
        cls,
        db,
        ma_chuyen_di,
        data,
        current_user
    ):
        chuyen_di = cls.check_owner(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

        data = cls.recalculate_distance_for_days(
            db=db,
            data=data
        )

        data = cls.recalculate_transport_cost_for_days(
            db=db,
            data=data
        )

        old_lich_trinhs = (
            db.query(LichTrinh)
            .filter(LichTrinh.ma_chuyen_di == ma_chuyen_di)
            .all()
        )

        for lich_trinh in old_lich_trinhs:
            db.delete(lich_trinh)

        db.flush()

        for day in data.days:
            ngay = chuyen_di.ngay_di + timedelta(
                days=day.day - 1
            )

            lich_trinh = LichTrinh(
                ma_chuyen_di=ma_chuyen_di,
                tieu_de=f"Ngày {day.day}",
                ngay=ngay
            )

            db.add(lich_trinh)
            db.flush()

            for item in day.items:
                chi_tiet = ChiTietLichTrinh(
                    ma_lich_trinh=lich_trinh.ma_lich_trinh,
                    ma_dia_diem=item.ma_dia_diem,
                    gio_bat_dau=cls.parse_time(item.start_time),
                    gio_ket_thuc=cls.parse_time(item.end_time),
                    ma_pt=item.ma_pt,
                    khoang_cach=cls.to_float(item.distance_km),
                    so_luong_pt=item.number_of_vehicles or 1,
                    gia=Decimal(
                        str(item.estimated_transport_cost or 0)
                    )
                )

                db.add(chi_tiet)

        chuyen_di.trang_thai = "da_chinh_sua"
        chuyen_di.ngay_cap_nhat = datetime.utcnow()

        db.commit()

        return cls.get_by_chuyen_di(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

    @classmethod
    def kiem_tra_doi_phuong_tien(
        cls,
        db,
        data
    ):
        phuong_tien = cls.get_vehicle_by_id(
            db=db,
            ma_pt=data.ma_pt_moi
        )

        if not phuong_tien:
            raise ValueError("Không tìm thấy phương tiện")

        distance_km = cls.to_float(data.distance_km)
        old_cost = cls.to_float(data.old_cost)
        so_nguoi = int(data.so_nguoi or 1)

        suc_chua = phuong_tien.suc_chua or 1
        gia_moi_km = cls.to_float(
            phuong_tien.gia_moi_km
        )

        number_of_vehicles = getattr(
            data,
            "number_of_vehicles",
            None
        )

        if number_of_vehicles and number_of_vehicles > 0:
            so_luong_pt = int(number_of_vehicles)
        else:
            so_luong_pt = math.ceil(
                so_nguoi / suc_chua
            )

        new_cost = distance_km * gia_moi_km * so_luong_pt
        new_cost = round(new_cost, 0)

        diff_cost = new_cost - old_cost
        is_increase = diff_cost > 0

        if is_increase:
            message = (
                f"Thay đổi phương tiện/số lượng xe sẽ tăng thêm "
                f"{diff_cost:,.0f} VNĐ. "
                f"Bạn có đồng ý không?"
            )
        else:
            message = (
                "Thay đổi phương tiện/số lượng xe không làm tăng chi phí."
            )

        return {
            "ma_pt_moi": str(phuong_tien.ma_pt),
            "ten_pt": phuong_tien.ten_pt,
            "distance_km": distance_km,
            "so_nguoi": so_nguoi,
            "suc_chua": suc_chua,
            "so_luong_pt": so_luong_pt,
            "number_of_vehicles": so_luong_pt,
            "gia_moi_km": gia_moi_km,
            "old_cost": old_cost,
            "new_cost": new_cost,
            "diff_cost": diff_cost,
            "is_increase": is_increase,
            "message": message
        }