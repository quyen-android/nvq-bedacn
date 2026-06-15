from app.services.khoang_cach_service import KhoangCachService


class RouteService:

    TIME_SLOT_ORDER = {
        "morning": 1,
        "lunch": 2,
        "afternoon": 3,
        "dinner": 4,
        "evening": 5
    }

    @classmethod
    def sort_by_time_slot(cls, places):
        return sorted(
            places,
            key=lambda p: cls.TIME_SLOT_ORDER.get(
                p.get("time_slot", "afternoon"),
                3
            )
        )

    @classmethod
    def optimize_group(cls, current_place, places):
        remaining_places = places.copy()
        route = []
        segments = []
        total_distance = 0

        while remaining_places:
            nearest_place = min(
                remaining_places,
                key=lambda p: KhoangCachService.distance_between_places(
                    current_place,
                    p
                )
            )

            distance = KhoangCachService.distance_between_places(
                current_place,
                nearest_place
            )

            segments.append({
                "from": current_place,
                "to": nearest_place,
                "distance": round(distance, 2)
            })

            total_distance += distance
            route.append(nearest_place)
            current_place = nearest_place
            remaining_places.remove(nearest_place)

        return route, segments, total_distance, current_place

    @classmethod
    def optimize_day_route(cls, accommodation, places):
        if not places:
            return {
                "route": [],
                "segments": [],
                "total_distance": 0
            }

        sorted_places = cls.sort_by_time_slot(places)

        grouped = {}

        for place in sorted_places:
            time_slot = place.get("time_slot", "afternoon")
            grouped.setdefault(time_slot, []).append(place)

        route = []
        segments = []
        total_distance = 0

        current_place = accommodation if accommodation else sorted_places[0]

        for time_slot in ["morning", "lunch", "afternoon", "dinner", "evening"]:
            group_places = grouped.get(time_slot, [])

            if not group_places:
                continue

            group_route, group_segments, group_distance, current_place = (
                cls.optimize_group(
                    current_place=current_place,
                    places=group_places
                )
            )

            route.extend(group_route)
            segments.extend(group_segments)
            total_distance += group_distance

        if accommodation and route:
            distance_back = KhoangCachService.distance_between_places(
                current_place,
                accommodation
            )

            segments.append({
                "from": current_place,
                "to": accommodation,
                "distance": round(distance_back, 2)
            })

            total_distance += distance_back

        return {
            "route": route,
            "segments": segments,
            "total_distance": round(total_distance, 2)
        }

    @classmethod
    def optimize_all_days(cls, days_plan):
        optimized_days = []

        for day in days_plan:
            result = cls.optimize_day_route(
                accommodation=day.get("accommodation"),
                places=day.get("places", [])
            )

            optimized_days.append({
                "day": day["day"],
                "accommodation": day.get("accommodation"),
                "places": result["route"],
                "segments": result["segments"],
                "total_distance": result["total_distance"],
                "locked_places": day.get("locked_places", [])
            })

        return optimized_days