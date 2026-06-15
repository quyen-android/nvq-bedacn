from app.services.khoang_cach_service import KhoangCachService


class ToiUuTuyenDuongService:

    @staticmethod
    def get_place_map(db_places):
        return {
            str(place.ma_dia_diem): place
            for place in db_places
        }

    @staticmethod
    def get_distance(item_a, item_b, place_map):
        place_a = place_map.get(
            str(item_a.get("id"))
        )

        place_b = place_map.get(
            str(item_b.get("id"))
        )

        if not place_a or not place_b:
            return 999999

        return KhoangCachService.distance_between_places(
            place_a,
            place_b
        )

    @classmethod
    def sap_xep_gan_nhat(
        cls,
        items,
        place_map
    ):
        if len(items) <= 2:
            return items

        accommodation_items = [
            item for item in items
            if item.get("type") == "accommodation"
        ]

        normal_items = [
            item for item in items
            if item.get("type") != "accommodation"
        ]

        if not normal_items:
            return items

        result = []

        current = normal_items.pop(0)
        result.append(current)

        while normal_items:
            nearest_item = min(
                normal_items,
                key=lambda item: cls.get_distance(
                    current,
                    item,
                    place_map
                )
            )

            normal_items.remove(
                nearest_item
            )

            result.append(
                nearest_item
            )

            current = nearest_item

        if accommodation_items:
            accommodation_item = min(
                accommodation_items,
                key=lambda item: cls.get_distance(
                    result[-1],
                    item,
                    place_map
                )
            )

            result.append(
                accommodation_item
            )

        return result

    @classmethod
    def toi_uu(cls, lich_trinh_ai, db_places):
        place_map = cls.get_place_map(
            db_places
        )

        days = lich_trinh_ai.get("days", [])

        for day in days:
            items = day.get("items", [])

            day["items"] = cls.sap_xep_gan_nhat(
                items,
                place_map
            )

        return lich_trinh_ai