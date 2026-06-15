from math import radians, cos, sin, asin, sqrt


class KhoangCachService:

    @staticmethod
    def haversine_km(lat1, lon1, lat2, lon2):
        try:
            lat1 = float(lat1)
            lon1 = float(lon1)
            lat2 = float(lat2)
            lon2 = float(lon2)

            if lat1 == 0 or lon1 == 0 or lat2 == 0 or lon2 == 0:
                return 999999

            lat1, lon1, lat2, lon2 = map(
                radians,
                [lat1, lon1, lat2, lon2]
            )

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = (
                sin(dlat / 2) ** 2
                + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
            )

            c = 2 * asin(sqrt(a))

            return c * 6371

        except Exception:
            return 999999

    @staticmethod
    def extract_coords(place):
        if isinstance(place, dict):
            metadata = place.get("metadata", {})

            lat = (
                metadata.get("lat")
                or metadata.get("vi_do")
                or place.get("lat")
                or place.get("vi_do")
                or 0
            )

            lon = (
                metadata.get("lon")
                or metadata.get("kinh_do")
                or place.get("lon")
                or place.get("kinh_do")
                or 0
            )

            return float(lat or 0), float(lon or 0)

        lat = (
            getattr(place, "vi_do", None)
            or getattr(place, "lat", None)
            or 0
        )

        lon = (
            getattr(place, "kinh_do", None)
            or getattr(place, "lon", None)
            or 0
        )

        return float(lat or 0), float(lon or 0)

    @classmethod
    def distance_between_places(cls, p1, p2):
        if not p1 or not p2:
            return 999999

        lat1, lon1 = cls.extract_coords(p1)
        lat2, lon2 = cls.extract_coords(p2)

        return cls.haversine_km(
            lat1,
            lon1,
            lat2,
            lon2
        )