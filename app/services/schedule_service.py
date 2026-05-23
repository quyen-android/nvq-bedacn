from datetime import datetime, timedelta, time


class ScheduleService:

    DEFAULT_DAY_START = time(8, 0)
    DEFAULT_DAY_END = time(21, 30)

    @staticmethod
    def get_metadata(place):
        return place.get("metadata", {})

    @staticmethod
    def get_place_id(place):
        metadata = place.get("metadata", {})
        return metadata.get("ma_dia_diem") or metadata.get("id")

    @staticmethod
    def get_visit_duration(place):
        metadata = ScheduleService.get_metadata(place)

        if metadata.get("thoi_gian_tham_quan_tb"):
            return int(metadata["thoi_gian_tham_quan_tb"])

        loai = (
            metadata.get("loai_dia_diem")
            or metadata.get("loai")
            or ""
        ).lower().strip()

        if loai == "quán ăn":
            return 75

        if loai == "chỗ ở":
            return 0

        return 120

    @staticmethod
    def to_datetime(base_date, value):
        if isinstance(value, datetime):
            return value

        if isinstance(value, time):
            return datetime.combine(base_date, value)

        if isinstance(value, str):
            hour, minute = value.split(":")[:2]
            return datetime.combine(
                base_date,
                time(int(hour), int(minute))
            )

        return None

    @classmethod
    def get_open_close_time(cls, place, base_date):
        metadata = cls.get_metadata(place)

        open_time = metadata.get("gio_mo") or cls.DEFAULT_DAY_START
        close_time = metadata.get("gio_dong") or cls.DEFAULT_DAY_END

        return (
            cls.to_datetime(base_date, open_time),
            cls.to_datetime(base_date, close_time)
        )

    @staticmethod
    def estimate_travel_minutes(segment):
        distance = float(segment.get("distance", 0))

        vehicle = segment.get("vehicle")
        speed = getattr(vehicle, "toc_do_tb", None) or 30

        if speed <= 0:
            speed = 30

        return round(distance / float(speed) * 60)

    @classmethod
    def build_locked_map(cls, locked_places, trip_date):
        locked_map = {}

        for item in locked_places:
            place = item["place"]
            place_id = cls.get_place_id(place)

            if not place_id:
                continue

            locked_map[place_id] = {
                "start": cls.to_datetime(trip_date, item["locked_start"]),
                "end": cls.to_datetime(trip_date, item["locked_end"])
            }

        return locked_map

    @staticmethod
    def is_accommodation(place):
        metadata = place.get("metadata", {})

        loai = (
            metadata.get("loai_dia_diem")
            or metadata.get("loai")
            or ""
        ).lower().strip()

        return loai == "chỗ ở"

    @classmethod
    def schedule_day(cls, day, trip_date):
        segments = day.get("segments", [])
        locked_places = day.get("locked_places", [])

        locked_map = cls.build_locked_map(
            locked_places=locked_places,
            trip_date=trip_date
        )

        current_time = datetime.combine(
            trip_date,
            cls.DEFAULT_DAY_START
        )

        schedule = []

        for segment in segments:
            place = segment["to"]

            if cls.is_accommodation(place):
                continue

            place_id = cls.get_place_id(place)

            travel_minutes = cls.estimate_travel_minutes(segment)

            arrive_time = current_time + timedelta(
                minutes=travel_minutes
            )

            open_time, close_time = cls.get_open_close_time(
                place,
                trip_date
            )

            duration = cls.get_visit_duration(place)

            is_golden_hour = place_id in locked_map

            if is_golden_hour:
                locked_start = locked_map[place_id]["start"]
                locked_end = locked_map[place_id]["end"]

                start_time = locked_start
                end_time = locked_end

                valid = (
                    arrive_time <= start_time
                    and start_time >= open_time
                    and end_time <= close_time
                )

            else:
                start_time = max(
                    arrive_time,
                    open_time
                )

                end_time = start_time + timedelta(
                    minutes=duration
                )

                valid = (
                    start_time >= open_time
                    and end_time <= close_time
                )

            schedule.append({
                "place": place,
                "start_time": start_time.strftime("%H:%M"),
                "end_time": end_time.strftime("%H:%M"),
                "travel_minutes": travel_minutes,
                "is_golden_hour": is_golden_hour,
                "valid": valid,
                "open_time": open_time.strftime("%H:%M"),
                "close_time": close_time.strftime("%H:%M")
            })

            current_time = end_time

        day["schedule"] = schedule

        day["schedule_valid"] = all(
            item["valid"]
            for item in schedule
        )

        return day

    @classmethod
    def schedule_all_days(cls, days_plan, start_date):
        result = []

        for day in days_plan:
            trip_date = start_date + timedelta(
                days=day["day"] - 1
            )

            result.append(
                cls.schedule_day(
                    day=day,
                    trip_date=trip_date
                )
            )

        return result