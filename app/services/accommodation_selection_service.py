from app.services.distance_service import DistanceService


class AccommodationSelectionService:

    @staticmethod
    def calculate_accommodation_score(
        accommodation,
        day_places
    ):
        if not day_places:
            return 999999

        total_distance = 0

        for place in day_places:
            total_distance += (
                DistanceService
                .distance_between_places(
                    accommodation,
                    place
                )
            )

        avg_distance = (
            total_distance
            / len(day_places)
        )

        ranking_score = (
            accommodation
            .get("ranking", {})
            .get("final_score", 0)
        )

        # điểm càng nhỏ càng tốt
        # ưu tiên gần trước, ranking phụ
        score = (
            avg_distance
            - ranking_score
        )

        return score

    @classmethod
    def select_accommodation_for_day(
        cls,
        accommodations,
        day_places
    ):
        if not accommodations:
            raise ValueError(
                "Không có danh sách chỗ ở để chọn"
            )

        selected_accommodation = min(
            accommodations,
            key=lambda accommodation: cls.calculate_accommodation_score(
                accommodation,
                day_places
            )
        )

        return selected_accommodation

    @classmethod
    def assign_accommodations_to_days(
        cls,
        accommodations,
        days_plan
    ):
        result = []

        for day in days_plan:
            day_places = day["places"]

            selected_accommodation = cls.select_accommodation_for_day(
                accommodations=accommodations,
                day_places=day_places
            )

            result.append({
                "day": day["day"],
                "accommodation": selected_accommodation,
                "places": day_places
            })

        return result