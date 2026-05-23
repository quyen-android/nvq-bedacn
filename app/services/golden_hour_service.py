from app.repositories import khung_gio_vang_repo
from datetime import timedelta

class GoldenHourService:

    @staticmethod
    def get_place_id(place):
        metadata = place.get("metadata", {})

        return (
            metadata.get("ma_dia_diem")
            or metadata.get("id")
        )

    @classmethod
    def get_golden_hour(cls, db, place, trip_date):
        ma_dia_diem = cls.get_place_id(place)

        if not ma_dia_diem:
            return None

        return (
            khung_gio_vang_repo
            .get_by_dia_diem_and_month(
                db=db,
                ma_dia_diem=ma_dia_diem,
                month=trip_date.month
            )
        )

    @classmethod
    def lock_golden_hour_places(cls, db, days_plan, start_date):
        result = []

        for day in days_plan:
            trip_date = start_date + timedelta(
                days=day["day"] - 1
            )

            locked_places = []
            normal_places = []

            for place in day.get("places", []):
                golden_hours = cls.get_golden_hour(
                    db=db,
                    place=place,
                    trip_date=trip_date
                )

                if golden_hours:
                    khung = golden_hours[0]

                    locked_places.append({
                        "place": place,
                        "golden_hour": khung,
                        "locked_start": khung.gio_bat_dau,
                        "locked_end": khung.gio_ket_thuc
                    })
                else:
                    normal_places.append(place)

            locked_places = sorted(
                locked_places,
                key=lambda item: item["locked_start"]
            )

            day["normal_places"] = normal_places
            day["locked_places"] = locked_places

            result.append(day)

        return result