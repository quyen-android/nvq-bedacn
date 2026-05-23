import math


class DistanceService:

    @staticmethod
    def haversine_km(
        lat1,
        lon1,
        lat2,
        lon2
    ):
        if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
            return 999999

        lat1 = float(lat1)
        lon1 = float(lon1)
        lat2 = float(lat2)
        lon2 = float(lon2)

        r = 6371

        dlat = math.radians(lat2 - lat1)
        dlon = math.radians(lon2 - lon1)

        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(math.radians(lat1))
            * math.cos(math.radians(lat2))
            * math.sin(dlon / 2) ** 2
        )

        c = 2 * math.asin(
            math.sqrt(a)
        )

        return r * c

    @classmethod
    def distance_between_places(
        cls,
        place_a,
        place_b
    ):
        meta_a = place_a.get("metadata", {})
        meta_b = place_b.get("metadata", {})

        return cls.haversine_km(
            meta_a.get("lat"),
            meta_a.get("lon"),
            meta_b.get("lat"),
            meta_b.get("lon")
        )