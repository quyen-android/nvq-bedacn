from math import ceil
from app.services.distance_service import DistanceService

class TripCostService:

    PHU_PHI = 0.1

    @staticmethod
    def get_metadata_price(place):
        if not place:
            return 0

        metadata = place.get("metadata", {})

        return float(
            metadata.get("gia_trung_binh")
            or metadata.get("gia")
            or 0
        )

    @staticmethod
    def get_place_type(place):
        if not place:
            return ""

        metadata = place.get("metadata", {})

        loai = (
            metadata.get("loai_dia_diem")
            or metadata.get("loai")
            or metadata.get("ten_loai")
            or ""
        )

        return loai.lower().strip()

    @staticmethod
    def get_vehicle_capacity(vehicle):
        return int(
            getattr(vehicle, "suc_chua", None)
            or getattr(vehicle, "so_nguoi", None)
            or 1
        )

    @staticmethod
    def get_vehicle_price_per_km(vehicle):
        return float(
            getattr(vehicle, "gia_moi_km", 0)
            or 0
        )

    @classmethod
    def calculate_vehicle_count(
        cls,
        so_nguoi,
        vehicle
    ):
        capacity = cls.get_vehicle_capacity(
            vehicle
        )

        return ceil(
            so_nguoi / capacity
        )

    @classmethod
    def calculate_transport_cost(
        cls,
        distance_km,
        so_nguoi,
        vehicle
    ):
        if not vehicle:
            return 0

        vehicle_count = cls.calculate_vehicle_count(
            so_nguoi=so_nguoi,
            vehicle=vehicle
        )

        price_per_km = cls.get_vehicle_price_per_km(
            vehicle
        )

        return (
            distance_km
            * price_per_km
            * vehicle_count
        )

    @classmethod
    def calculate_intercity_cost(
        cls,
        chuyen_di
    ):
        tinh_di = chuyen_di.tinh_di
        tinh_den = chuyen_di.tinh_den
        vehicle = chuyen_di.phuong_tien

        if not tinh_di or not tinh_den or not vehicle:
            return {
                "distance": 0,
                "cost": 0,
                "vehicle": None
            }

        one_way_distance = DistanceService.haversine_km(
            tinh_di.vi_do,
            tinh_di.kinh_do,
            tinh_den.vi_do,
            tinh_den.kinh_do
        )

        round_trip_distance = one_way_distance * 2

        cost = cls.calculate_transport_cost(
            distance_km=round_trip_distance,
            so_nguoi=chuyen_di.so_nguoi,
            vehicle=vehicle
        )

        return {
            "distance": round(round_trip_distance, 2),
            "cost": round(cost, 0),
            "vehicle": vehicle.ten_pt
        }

    @classmethod
    def calculate_accommodation_cost(
        cls,
        accommodation,
        so_nguoi
    ):
        if not accommodation:
            return 0

        price_per_room = cls.get_metadata_price(
            accommodation
        )

        room_capacity = 3

        room_count = ceil(
            so_nguoi / room_capacity
        )

        return price_per_room * room_count

    @classmethod
    def calculate_places_cost(
        cls,
        places,
        so_nguoi
    ):
        food_cost = 0
        attraction_cost = 0
        other_cost = 0

        for place in places:
            place_type = cls.get_place_type(place)
            price = cls.get_metadata_price(place)

            if place_type == "quán ăn":
                food_cost += price * so_nguoi

            elif place_type == "điểm tham quan":
                attraction_cost += price * so_nguoi

            else:
                other_cost += price * so_nguoi

        return {
            "food_cost": food_cost,
            "attraction_cost": attraction_cost,
            "other_cost": other_cost
        }

    @classmethod
    def calculate_day_cost(
        cls,
        day,
        so_nguoi
    ):
        accommodation = day.get("accommodation")
        places = day.get("places", [])

        accommodation_cost = cls.calculate_accommodation_cost(
            accommodation=accommodation,
            so_nguoi=so_nguoi
        )

        places_cost = cls.calculate_places_cost(
            places=places,
            so_nguoi=so_nguoi
        )

        local_transport_cost = day.get(
            "local_transport_cost",
            0
        )

        total_day_cost = (
            accommodation_cost
            + places_cost["food_cost"]
            + places_cost["attraction_cost"]
            + places_cost["other_cost"]
            + local_transport_cost
        )

        day["cost"] = {
            "accommodation_cost": round(accommodation_cost, 0),
            "food_cost": round(places_cost["food_cost"], 0),
            "attraction_cost": round(places_cost["attraction_cost"], 0),
            "other_cost": round(places_cost["other_cost"], 0),
            "local_transport_cost": round(local_transport_cost, 0),
            "total_day_cost": round(total_day_cost, 0)
        }

        return day

    @classmethod
    def calculate_trip_cost(
        cls,
        days_plan,
        chuyen_di
    ):
        intercity = cls.calculate_intercity_cost(
            chuyen_di=chuyen_di
        )

        total_days_cost = 0
        result_days = []

        for day in days_plan:
            day = cls.calculate_day_cost(
                day=day,
                so_nguoi=chuyen_di.so_nguoi
            )

            total_days_cost += day["cost"]["total_day_cost"]
            result_days.append(day)

        subtotal = (
            intercity["cost"]
            + total_days_cost
        )

        extra_fee = subtotal * cls.PHU_PHI

        total_cost = subtotal + extra_fee

        budget = float(
            chuyen_di.ngan_sach or 0
        )

        return {
            "days_plan": result_days,
            "cost_summary": {
                "intercity_vehicle": intercity["vehicle"],
                "intercity_distance": intercity["distance"],
                "intercity_transport_cost": intercity["cost"],
                "days_cost": round(total_days_cost, 0),
                "extra_fee": round(extra_fee, 0),
                "total_cost": round(total_cost, 0),
                "budget": budget,
                "is_over_budget": total_cost > budget,
                "over_budget_amount": round(
                    max(total_cost - budget, 0),
                    0
                ),
                "remaining_budget": round(
                    max(budget - total_cost, 0),
                    0
                )
            }
        }