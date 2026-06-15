from datetime import datetime


class KiemTraLichTrinhService:

    @staticmethod
    def parse_time(value):
        if not value or value == "overnight":
            return None

        try:
            return datetime.strptime(
                value,
                "%H:%M"
            ).time()
        except Exception:
            return None

    @classmethod
    def kiem_tra(
        cls,
        lich_trinh_ai,
        db_places,
        db_vehicles,
        so_ngay,
        so_nguoi
    ):
        loi = []

        if not lich_trinh_ai:
            return ["Lịch trình rỗng"]

        days = lich_trinh_ai.get("days", [])

        if len(days) != so_ngay:
            loi.append(
                f"Số ngày không đúng. Yêu cầu {so_ngay}, AI trả {len(days)}"
            )

        place_ids = {
            str(place.ma_dia_diem)
            for place in db_places
        }

        vehicle_map = {
            str(vehicle.ma_pt): vehicle
            for vehicle in db_vehicles
        }

        da_dung_dia_diem = set()

        for day in days:
            ngay = day.get("day")
            items = day.get("items", [])

            if not items:
                loi.append(f"Ngày {ngay} không có địa điểm")
                continue

            cho_o_items = [
                item for item in items
                if item.get("type") == "accommodation"
            ]

            if len(cho_o_items) != 1:
                loi.append(
                    f"Ngày {ngay} phải có đúng 1 chỗ ở"
                )

            if items[-1].get("type") != "accommodation":
                loi.append(
                    f"Ngày {ngay}: chỗ ở phải là địa điểm cuối cùng"
                )

            for item in items:
                ma_dia_diem = str(item.get("id", ""))
                ma_pt = str(item.get("ma_pt", ""))

                if ma_dia_diem not in place_ids:
                    loi.append(
                        f"Ngày {ngay}: địa điểm {ma_dia_diem} không tồn tại"
                    )

                if item.get("type") != "accommodation":
                    if ma_dia_diem in da_dung_dia_diem:
                        loi.append(
                            f"Ngày {ngay}: địa điểm {ma_dia_diem} bị trùng"
                        )
                    else:
                        da_dung_dia_diem.add(ma_dia_diem)

                if ma_pt not in vehicle_map:
                    loi.append(
                        f"Ngày {ngay}: phương tiện {ma_pt} không tồn tại"
                    )
                    continue

                phuong_tien = vehicle_map[ma_pt]

                so_xe = int(
                    item.get("number_of_vehicles") or 1
                )

                suc_chua = int(
                    phuong_tien.suc_chua or 1
                )

                if suc_chua * so_xe < so_nguoi:
                    loi.append(
                        f"Ngày {ngay}: phương tiện {phuong_tien.ten_pt} không đủ sức chứa"
                    )

                start_time = cls.parse_time(
                    item.get("start_time")
                )

                end_time = cls.parse_time(
                    item.get("end_time")
                )

                if item.get("type") != "accommodation":
                    if not start_time or not end_time:
                        loi.append(
                            f"Ngày {ngay}: thời gian của {ma_dia_diem} không hợp lệ"
                        )
                    elif end_time <= start_time:
                        loi.append(
                            f"Ngày {ngay}: giờ kết thúc phải sau giờ bắt đầu"
                        )

        return loi

    @classmethod
    def hop_le(
        cls,
        lich_trinh_ai,
        db_places,
        db_vehicles,
        so_ngay,
        so_nguoi
    ):
        loi = cls.kiem_tra(
            lich_trinh_ai=lich_trinh_ai,
            db_places=db_places,
            db_vehicles=db_vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi
        )

        return len(loi) == 0