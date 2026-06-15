from datetime import datetime


class KiemTraGioMoCuaService:

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

    @staticmethod
    def get_place_map(db_places):
        return {
            str(place.ma_dia_diem): place
            for place in db_places
        }

    @classmethod
    def kiem_tra(cls, lich_trinh_ai, db_places):
        loi = []

        place_map = cls.get_place_map(
            db_places
        )

        days = lich_trinh_ai.get("days", [])

        for day in days:
            ngay = day.get("day")
            items = day.get("items", [])

            for item in items:
                if item.get("type") == "accommodation":
                    continue

                ma_dia_diem = str(
                    item.get("id", "")
                )

                dia_diem = place_map.get(
                    ma_dia_diem
                )

                if not dia_diem:
                    continue

                gio_mo = dia_diem.gio_mo
                gio_dong = dia_diem.gio_dong

                if not gio_mo or not gio_dong:
                    continue

                start_time = cls.parse_time(
                    item.get("start_time")
                )

                end_time = cls.parse_time(
                    item.get("end_time")
                )

                if not start_time or not end_time:
                    loi.append(
                        f"Ngày {ngay}: {dia_diem.ten} có thời gian không hợp lệ"
                    )
                    continue

                if start_time < gio_mo:
                    loi.append(
                        f"Ngày {ngay}: {dia_diem.ten} bắt đầu trước giờ mở cửa"
                    )

                if end_time > gio_dong:
                    loi.append(
                        f"Ngày {ngay}: {dia_diem.ten} kết thúc sau giờ đóng cửa"
                    )

        return loi