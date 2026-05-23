class PlaceSplitService:

    @staticmethod
    def split_places(ranked_places):
        accommodations = []
        travel_places = []

        for place in ranked_places:
            loai = (
                place["metadata"]
                .get("loai", "")
                .lower()
                .strip()
            )

            if loai == "chỗ ở":
                accommodations.append(place)
            else:
                travel_places.append(place)

        return {
            "accommodations": accommodations,
            "travel_places": travel_places
        }