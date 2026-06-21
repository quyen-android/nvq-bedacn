from math import ceil

from app.services.khoang_cach_service import KhoangCachService


class DuToanChiPhiService:

    @staticmethod
    def get_place_map(db_places):
        return {
            str(place.ma_dia_diem): place
            for place in db_places
        }

    @staticmethod
    def get_vehicle_map(db_vehicles):
        return {
            str(vehicle.ma_pt): vehicle
            for vehicle in db_vehicles
        }

    @staticmethod
    def get_so_xe(so_nguoi, suc_chua):
        so_nguoi = int(so_nguoi or 1)
        suc_chua = int(suc_chua or 1)

        return ceil(so_nguoi / suc_chua)

    @staticmethod
    def get_so_phong(so_nguoi):
        try:
            so_nguoi = int(so_nguoi or 1)
        except Exception:
            so_nguoi = 1

        return ceil(so_nguoi/ 2)

    @classmethod
    def tinh_chi_phi_item(
        cls,
        item,
        place,
        so_nguoi
    ):
        gia = float(
            place.gia_trung_binh or 0
        )

        loai = ""

        if place.loai:
            loai = str(
                place.loai.ten_loai or ""
            ).strip().lower()

        if loai == "chỗ ở":
            so_phong = cls.get_so_phong(
                so_nguoi
            )

            return {
                "loai_chi_phi": "luu_tru",
                "so_phong": so_phong,
                "so_nguoi": int(so_nguoi or 1),
                "don_gia": gia,
                "chi_phi": gia * so_phong
            }

        if loai == "quán ăn":
            return {
                "loai_chi_phi": "an_uong",
                "so_nguoi": int(so_nguoi or 1),
                "don_gia": gia,
                "chi_phi": gia * int(so_nguoi or 1)
            }

        if loai == "điểm tham quan":
            return {
                "loai_chi_phi": "tham_quan",
                "so_nguoi": int(so_nguoi or 1),
                "don_gia": gia,
                "chi_phi": gia * int(so_nguoi or 1)
            }

        return None

    @classmethod
    def tinh_chi_phi_di_chuyen_item(
        cls,
        item_truoc,
        item_hien_tai,
        place_map,
        vehicle_map,
        so_nguoi
    ):
        if not item_truoc:
            return {
                "khoang_cach_km": 0,
                "chi_phi": 0,
                "segment": None
            }

        place_1 = place_map.get(
            str(item_truoc.get("id"))
        )

        place_2 = place_map.get(
            str(item_hien_tai.get("id"))
        )

        if not place_1 or not place_2:
            return {
                "khoang_cach_km": 0,
                "chi_phi": 0,
                "segment": None
            }

        ma_pt = str(
            item_hien_tai.get("ma_pt", "")
        )

        vehicle = vehicle_map.get(
            ma_pt
        )

        if not vehicle:
            return {
                "khoang_cach_km": 0,
                "chi_phi": 0,
                "segment": None
            }

        khoang_cach = KhoangCachService.distance_between_places(
            place_1,
            place_2
        )

        so_xe = int(
            item_hien_tai.get("number_of_vehicles") or 0
        )

        if so_xe <= 0:
            so_xe = cls.get_so_xe(
                so_nguoi,
                vehicle.suc_chua
            )

        chi_phi = (
            khoang_cach
            * float(vehicle.gia_moi_km or 0)
            * so_xe
        )

        segment = {
            "from_item_id": str(item_truoc.get("id")),
            "from_name": item_truoc.get("place_name"),
            "to_item_id": str(item_hien_tai.get("id")),
            "to_name": item_hien_tai.get("place_name"),
            "ma_pt": ma_pt,
            "transport_name": vehicle.ten_pt,
            "number_of_vehicles": so_xe,
            "distance_km": round(khoang_cach, 2),
            "estimated_transport_cost": round(chi_phi, 0)
        }

        return {
            "khoang_cach_km": khoang_cach,
            "chi_phi": chi_phi,
            "segment": segment
        }

    @classmethod
    def tinh_du_toan(
        cls,
        lich_trinh_ai,
        db_places,
        db_vehicles,
        so_nguoi,
        ngan_sach
    ):
        place_map = cls.get_place_map(
            db_places
        )

        vehicle_map = cls.get_vehicle_map(
            db_vehicles
        )

        tong_an_uong = 0
        tong_tham_quan = 0
        tong_luu_tru = 0
        tong_di_chuyen = 0

        all_segments = []

        days = lich_trinh_ai.get("days", [])

        item_cuoi_ngay_truoc = None

        for day in days:
            items = day.get("items", [])

            item_truoc = item_cuoi_ngay_truoc

            day_item_cost = 0
            day_transport_cost = 0
            day_segments = []

            for item in items:
                place = place_map.get(
                    str(item.get("id"))
                )

                if not place:
                    item_truoc = item
                    continue

                item_cost = cls.tinh_chi_phi_item(
                    item=item,
                    place=place,
                    so_nguoi=so_nguoi
                )

                chi_phi_item = float(
                    item_cost["chi_phi"]
                )

                loai_chi_phi = item_cost["loai_chi_phi"]

                if loai_chi_phi == "an_uong":
                    tong_an_uong += chi_phi_item
                elif loai_chi_phi == "tham_quan":
                    tong_tham_quan += chi_phi_item
                elif loai_chi_phi == "luu_tru":
                    tong_luu_tru += chi_phi_item

                transport_result = cls.tinh_chi_phi_di_chuyen_item(
                    item_truoc=item_truoc,
                    item_hien_tai=item,
                    place_map=place_map,
                    vehicle_map=vehicle_map,
                    so_nguoi=so_nguoi
                )

                chi_phi_di_chuyen = float(
                    transport_result["chi_phi"]
                )

                tong_di_chuyen += chi_phi_di_chuyen
                day_transport_cost += chi_phi_di_chuyen

                if transport_result["segment"]:
                    day_segments.append(
                        transport_result["segment"]
                    )

                    all_segments.append(
                        transport_result["segment"]
                    )

                item["estimated_cost"] = round(
                    chi_phi_item,
                    0
                )

                item["estimated_transport_cost"] = round(
                    chi_phi_di_chuyen,
                    0
                )

                item["estimated_total_cost_to_item"] = round(
                    chi_phi_item + chi_phi_di_chuyen,
                    0
                )

                item["cost_type"] = loai_chi_phi
                item["unit_price"] = round(
                    item_cost.get("don_gia", 0),
                    0
                )

                if loai_chi_phi == "luu_tru":
                    item["number_of_rooms"] = item_cost.get(
                        "so_phong",
                        1
                    )

                day_item_cost += chi_phi_item

                item_truoc = item

            if items:
                item_cuoi_ngay_truoc = items[-1]

            day["travel_segments"] = day_segments

            day["estimated_item_cost"] = round(
                day_item_cost,
                0
            )

            day["estimated_transport_cost"] = round(
                day_transport_cost,
                0
            )

            day["estimated_day_cost"] = round(
                day_item_cost + day_transport_cost,
                0
            )

        tong_chi_phi = (
            tong_an_uong
            + tong_tham_quan
            + tong_luu_tru
            + tong_di_chuyen
        )

        ngan_sach = float(
            ngan_sach or 0
        )

        vuot_ngan_sach = (
            tong_chi_phi > ngan_sach
            if ngan_sach > 0
            else False
        )

        so_tien_vuot = max(
            tong_chi_phi - ngan_sach,
            0
        )

        so_tien_con_lai = max(
            ngan_sach - tong_chi_phi,
            0
        )

        lich_trinh_ai["cost_summary"] = {
            "chi_phi_an_uong": round(tong_an_uong, 0),
            "chi_phi_tham_quan": round(tong_tham_quan, 0),
            "chi_phi_luu_tru": round(tong_luu_tru, 0),
            "chi_phi_di_chuyen_dia_phuong": round(tong_di_chuyen, 0),
            "tong_chi_phi": round(tong_chi_phi, 0),
            "ngan_sach": round(ngan_sach, 0),
            "vuot_ngan_sach": vuot_ngan_sach,
            "so_tien_vuot": round(so_tien_vuot, 0),
            "so_tien_con_lai": round(so_tien_con_lai, 0),
            "travel_segments": all_segments
        }

        lich_trinh_ai["estimated_total_cost"] = round(
            tong_chi_phi,
            0
        )

        lich_trinh_ai["budget_note"] = (
            f"Vượt ngân sách {round(so_tien_vuot, 0)} VNĐ"
            if vuot_ngan_sach
            else f"Còn lại {round(so_tien_con_lai, 0)} VNĐ"
        )

        return lich_trinh_ai