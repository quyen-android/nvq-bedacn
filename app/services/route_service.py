from app.services.distance_service import DistanceService


class RouteService:

    @classmethod
    def optimize_day_route(
        cls,
        accommodation,
        places
    ):
        if not places:
            return {
                "route": [],
                "segments": [],
                "total_distance": 0
            }

        if not accommodation:
            return {
                "route": places,
                "segments": [],
                "total_distance": 0
            }

        remaining_places = places.copy()
        route = []
        segments = []
        total_distance = 0

        current_place = accommodation

        while remaining_places:
            nearest_place = min(
                remaining_places,
                key=lambda place: (
                    DistanceService
                    .distance_between_places(
                        current_place,
                        place
                    )
                )
            )

            distance = (
                DistanceService
                .distance_between_places(
                    current_place,
                    nearest_place
                )
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

        # quay về chỗ ở
        distance_back = (
            DistanceService
            .distance_between_places(
                current_place,
                accommodation
            )
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
    def optimize_all_days(
        cls,
        days_plan
    ):
        optimized_days = []

        for day in days_plan:
            accommodation = day.get("accommodation")
            places = day.get("places", [])

            result = cls.optimize_day_route(
                accommodation=accommodation,
                places=places
            )

            optimized_days.append({
                "day": day["day"],
                "accommodation": accommodation,
                "places": result["route"],
                "segments": result["segments"],
                "total_distance": result["total_distance"]
            })

        return optimized_days