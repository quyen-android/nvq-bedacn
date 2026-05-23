class DaySplitService:

    @staticmethod
    def split_places_by_days(
        travel_places,
        so_ngay,
        max_places_per_day=4
    ):
        days_plan = []

        used_ids = set()

        for day_index in range(so_ngay):

            day_places = []

            for place in travel_places:

                metadata = place.get("metadata", {})

                place_id = (
                    metadata.get("id")
                    or metadata.get("ma_dia_diem")
                    or metadata.get("ten")
                )

                if place_id in used_ids:
                    continue

                if len(day_places) >= max_places_per_day:
                    break

                day_places.append(place)
                used_ids.add(place_id)

            days_plan.append({
                "day": day_index + 1,
                "places": day_places
            })

        return days_plan