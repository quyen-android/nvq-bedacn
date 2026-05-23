from math import ceil


class LocalTransportSelectionService:

    @staticmethod
    def get_capacity(vehicle):
        return int(
            getattr(vehicle, "suc_chua", None)
            or getattr(vehicle, "so_nguoi", None)
            or 1
        )

    @staticmethod
    def get_price_per_km(vehicle):
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
        capacity = cls.get_capacity(vehicle)

        return ceil(
            so_nguoi / capacity
        )

    @classmethod
    def calculate_segment_cost(
        cls,
        distance_km,
        so_nguoi,
        vehicle
    ):
        vehicle_count = cls.calculate_vehicle_count(
            so_nguoi=so_nguoi,
            vehicle=vehicle
        )

        price_per_km = cls.get_price_per_km(
            vehicle
        )

        cost = (
            distance_km
            * price_per_km
            * vehicle_count
        )

        return {
            "vehicle": vehicle,
            "vehicle_count": vehicle_count,
            "cost": cost
        }

    @classmethod
    def select_vehicle_for_segment(
        cls,
        vehicles,
        distance_km,
        so_nguoi
    ):
        if not vehicles:
            return None

        candidates = []

        for vehicle in vehicles:
            result = cls.calculate_segment_cost(
                distance_km=distance_km,
                so_nguoi=so_nguoi,
                vehicle=vehicle
            )

            candidates.append(result)

        return min(
            candidates,
            key=lambda item: item["cost"]
        )

    @classmethod
    def assign_vehicles_to_day_segments(
        cls,
        day,
        vehicles,
        so_nguoi
    ):
        total_local_transport_cost = 0

        for segment in day.get("segments", []):
            selected = cls.select_vehicle_for_segment(
                vehicles=vehicles,
                distance_km=segment["distance"],
                so_nguoi=so_nguoi
            )

            if not selected:
                segment["vehicle"] = None
                segment["vehicle_count"] = 0
                segment["cost"] = 0
                continue

            vehicle = selected["vehicle"]

            segment["vehicle"] = vehicle
            segment["vehicle_name"] = vehicle.ten_pt
            segment["vehicle_count"] = selected["vehicle_count"]
            segment["cost"] = round(selected["cost"], 0)

            total_local_transport_cost += selected["cost"]

        day["local_transport_cost"] = round(
            total_local_transport_cost,
            0
        )

        return day

    @classmethod
    def assign_vehicles_to_all_days(
        cls,
        days_plan,
        vehicles,
        so_nguoi
    ):
        result = []

        for day in days_plan:
            day = cls.assign_vehicles_to_day_segments(
                day=day,
                vehicles=vehicles,
                so_nguoi=so_nguoi
            )

            result.append(day)

        return result