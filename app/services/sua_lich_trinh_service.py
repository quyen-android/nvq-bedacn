from math import ceil


class SuaLichTrinhService:

    @staticmethod
    def lay_phuong_tien_mac_dinh(db_vehicles, so_nguoi):
        vehicles = [
            v for v in db_vehicles
            if v.loai != "lien_tinh"
        ]

        if not vehicles:
            return None

        vehicles = sorted(
            vehicles,
            key=lambda v: (
                ceil(so_nguoi / int(v.suc_chua or 1))
                * float(v.gia_moi_km or 0)
            )
        )

        return vehicles[0]

    @staticmethod
    def lay_cho_o_mac_dinh(db_places):
        for place in db_places:
            loai = ""

            if place.loai:
                loai = str(place.loai.ten_loai).strip().lower()

            if loai == "chỗ ở":
                return place

        return None

    @staticmethod
    def item_cho_o_mac_dinh(place, phuong_tien, so_nguoi):
        so_xe = ceil(
            so_nguoi / int(phuong_tien.suc_chua or 1)
        )

        return {
            "id": str(place.ma_dia_diem),
            "place_name": place.ten,
            "type": "accommodation",
            "start_time": "21:00",
            "end_time": "overnight",
            "time_slot": "evening",
            "is_golden_hour_used": False,
            "golden_hour_note": "Không áp dụng cho chỗ ở",
            "ma_pt": str(phuong_tien.ma_pt),
            "suggested_transport_name": phuong_tien.ten_pt,
            "number_of_vehicles": so_xe,
            "estimated_cost": float(place.gia_trung_binh or 0),
            "note": "Chỗ ở qua đêm, được hệ thống bổ sung"
        }

    @classmethod
    def sua(
        cls,
        lich_trinh_ai,
        db_places,
        db_vehicles,
        so_ngay,
        so_nguoi
    ):
        if not lich_trinh_ai:
            lich_trinh_ai = {}

        days = lich_trinh_ai.get("days", [])

        phuong_tien_mac_dinh = cls.lay_phuong_tien_mac_dinh(
            db_vehicles,
            so_nguoi
        )

        cho_o_mac_dinh = cls.lay_cho_o_mac_dinh(
            db_places
        )

        if not phuong_tien_mac_dinh:
            raise ValueError("Không có phương tiện địa phương để sửa lịch trình")

        if not cho_o_mac_dinh:
            raise ValueError("Không có chỗ ở để sửa lịch trình")

        while len(days) < so_ngay:
            days.append({
                "day": len(days) + 1,
                "items": []
            })

        days = days[:so_ngay]

        da_dung_dia_diem = set()

        for day in days:
            items = day.get("items", [])

            items_sach = []

            for item in items:
                ma_dia_diem = str(item.get("id", ""))

                if item.get("type") != "accommodation":
                    if ma_dia_diem in da_dung_dia_diem:
                        continue

                    da_dung_dia_diem.add(ma_dia_diem)

                ma_pt = item.get("ma_pt")

                if not ma_pt:
                    item["ma_pt"] = str(
                        phuong_tien_mac_dinh.ma_pt
                    )
                    item["suggested_transport_name"] = (
                        phuong_tien_mac_dinh.ten_pt
                    )

                so_xe = int(
                    item.get("number_of_vehicles") or 1
                )

                suc_chua = int(
                    phuong_tien_mac_dinh.suc_chua or 1
                )

                if suc_chua * so_xe < so_nguoi:
                    item["number_of_vehicles"] = ceil(
                        so_nguoi / suc_chua
                    )

                items_sach.append(item)

            items_khong_phai_cho_o = [
                item for item in items_sach
                if item.get("type") != "accommodation"
            ]

            cho_o_items = [
                item for item in items_sach
                if item.get("type") == "accommodation"
            ]

            if cho_o_items:
                cho_o_item = cho_o_items[0]
            else:
                cho_o_item = cls.item_cho_o_mac_dinh(
                    cho_o_mac_dinh,
                    phuong_tien_mac_dinh,
                    so_nguoi
                )

            day["items"] = (
                items_khong_phai_cho_o
                + [cho_o_item]
            )

            day["estimated_day_cost"] = sum(
                float(item.get("estimated_cost") or 0)
                for item in day["items"]
            )

        lich_trinh_ai["days"] = days

        lich_trinh_ai["estimated_total_cost"] = sum(
            float(day.get("estimated_day_cost") or 0)
            for day in days
        )

        if not lich_trinh_ai.get("budget_note"):
            lich_trinh_ai["budget_note"] = (
                "Lịch trình đã được hệ thống kiểm tra và sửa cơ bản"
            )

        return lich_trinh_ai