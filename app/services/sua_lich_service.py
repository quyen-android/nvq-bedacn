class SuaLichService:

    @staticmethod
    def repair_invalid_days(days_plan):
        for day in days_plan:
            if day.get("schedule_valid", True):
                continue

            invalid_items = [
                item for item in day.get("schedule", [])
                if not item.get("valid")
            ]

            day["canh_bao"] = [
                {
                    "dia_diem": item["place"]["metadata"].get("ten"),
                    "ly_do": (
                        "Không phù hợp giờ mở cửa hoặc không kịp khung giờ vàng"
                    ),
                    "gio_mo": item.get("open_time"),
                    "gio_dong": item.get("close_time")
                }
                for item in invalid_items
            ]

        return days_plan