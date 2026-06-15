class KiemTraAIService:

    @staticmethod
    def validate_ai_itinerary(ai_itinerary, so_ngay, travel_places):
        if not ai_itinerary:
            raise ValueError("Ollama không trả về lịch trình")

        if "days" not in ai_itinerary:
            raise ValueError("Ollama trả về thiếu trường days")

        days = ai_itinerary["days"]

        if len(days) != so_ngay:
            raise ValueError(
                f"Ollama trả về {len(days)} ngày, yêu cầu {so_ngay} ngày"
            )

        valid_ids = {
            str(place["ma_dia_diem"])
            for place in travel_places
        }

        used_ids = set()

        for day in days:
            if "day" not in day:
                raise ValueError("Một ngày bị thiếu trường day")

            if "places" not in day:
                raise ValueError("Một ngày bị thiếu trường places")

            for place in day["places"]:
                place_id = str(place.get("id"))

                if place_id not in valid_ids:
                    raise ValueError(
                        f"Ollama trả về địa điểm không tồn tại: {place_id}"
                    )

                if place_id in used_ids:
                    raise ValueError(
                        f"Ollama chọn trùng địa điểm: {place_id}"
                    )

                used_ids.add(place_id)

        return True