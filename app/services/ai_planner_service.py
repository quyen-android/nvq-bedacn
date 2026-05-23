from app.repositories import chuyen_di_repo
from app.services.golden_hour_service import GoldenHourService
from app.services.rag_service import RagService
from app.services.place_ranking_service import PlaceRankingService
from app.services.place_split_service import PlaceSplitService
from app.services.day_split_service import DaySplitService
from app.services.accommodation_selection_service import AccommodationSelectionService
from app.services.route_service import RouteService
from app.services.trip_cost_service import TripCostService
from app.repositories import phuong_tien_repo
from app.services.local_transport_selection_service import LocalTransportSelectionService
from app.services.trip_cost_service import TripCostService
from app.services.schedule_service import ScheduleService

class AIPlannerService:

    @staticmethod
    def build_search_query(
        chuyen_di,
        loai_du_lich_list,
        so_thich_am_thuc_list,
        yeu_cau_dac_biet_list
    ):
        loai_du_lich_text = ", ".join(
            item[0] for item in loai_du_lich_list
        )

        so_thich_am_thuc_text = ", ".join(
            item[0] for item in so_thich_am_thuc_list
        )

        yeu_cau_dac_biet_text = ", ".join(
            item[0] for item in yeu_cau_dac_biet_list
        )

        query = f"""
        Tên chuyến đi:
        {chuyen_di.ten_chuyen_di}

        Tỉnh đến:
        {chuyen_di.tinh_den.ten_tinh if chuyen_di.tinh_den else ""}

        Số người:
        {chuyen_di.so_nguoi}

        Ngân sách:
        {chuyen_di.ngan_sach}

        Ngày đi:
        {chuyen_di.ngay_di}

        Ngày về:
        {chuyen_di.ngay_ve}

        Loại du lịch:
        {loai_du_lich_text}

        Sở thích ẩm thực:
        {so_thich_am_thuc_text}

        Yêu cầu đặc biệt:
        {yeu_cau_dac_biet_text}
        """

        return query

    @classmethod
    def generate_plan(
        cls,
        db,
        ma_chuyen_di
    ):
        
        # 1. Lấy chuyến đi
        chuyen_di = chuyen_di_repo.get_by_id(
            db,
            ma_chuyen_di
        )

        if not chuyen_di:
            raise ValueError(
                "Không tìm thấy chuyến đi"
            )

        # 2. Tính số ngày
        so_ngay = (
            chuyen_di.ngay_ve
            - chuyen_di.ngay_di
        ).days + 1

        if so_ngay <= 0:
            raise ValueError(
                "Ngày về phải lớn hơn hoặc bằng ngày đi"
            )
        
        # 3. Tạo query cho Chroma
        loai_du_lich_list = chuyen_di_repo.get_loai_du_lich_by_chuyen_di(
            db,
            ma_chuyen_di
        )

        so_thich_am_thuc_list = chuyen_di_repo.get_so_thich_am_thuc_by_chuyen_di(
            db,
            ma_chuyen_di
        )

        yeu_cau_dac_biet_list = chuyen_di_repo.get_yeu_cau_dac_biet_by_chuyen_di(
            db,
            ma_chuyen_di
        )

        search_query = cls.build_search_query(
            chuyen_di=chuyen_di,
            loai_du_lich_list=loai_du_lich_list,
            so_thich_am_thuc_list=so_thich_am_thuc_list,
            yeu_cau_dac_biet_list=yeu_cau_dac_biet_list
        )

        # 4. Search địa điểm bằng RAG
        places = RagService.search_places(
            query=search_query,
            so_ngay=so_ngay
        )

        # 5. Chỉ lấy địa điểm thuộc tỉnh đến
        if chuyen_di.tinh_den:
            ten_tinh_den = (
                chuyen_di
                .tinh_den
                .ten_tinh
            )

            places = [
                place
                for place in places
                if place["metadata"].get("tinh") == ten_tinh_den
            ]

        # 6. Ranking địa điểm
        ranked_places = (
            PlaceRankingService
            .rank_places(
                places=places
            )
        )

        # 7. Tách hotel và địa điểm đi chơi
        split_result = (
            PlaceSplitService
            .split_places(
                ranked_places=ranked_places
            )
        )

        accommodations = split_result["accommodations"]
        travel_places = split_result["travel_places"]

        # 8. Chia địa điểm đi chơi vào từng ngày
        days_plan = (
            DaySplitService
            .split_places_by_days(
                travel_places=travel_places,
                so_ngay=so_ngay,
                max_places_per_day=4
            )
        )

        days_plan = (
            GoldenHourService
            .lock_golden_hour_places(
                db=db,
                days_plan=days_plan,
                start_date=chuyen_di.ngay_di
            )
        )

        days_plan = (
            AccommodationSelectionService
            .assign_accommodations_to_days(
                accommodations=accommodations,
                days_plan=days_plan
            )
        )

        days_plan = (
            RouteService
            .optimize_all_days(
                days_plan=days_plan
            )
        )

        local_vehicles = (
            phuong_tien_repo
            .get_all_local_vehicles(db)
        )

        days_plan = (
            LocalTransportSelectionService
            .assign_vehicles_to_all_days(
                days_plan=days_plan,
                vehicles=local_vehicles,
                so_nguoi=chuyen_di.so_nguoi
            )
        )

        days_plan = (
            ScheduleService
            .schedule_all_days(
                days_plan=days_plan,
                start_date=chuyen_di.ngay_di
            )
        )

        cost_result = (
            TripCostService
            .calculate_trip_cost(
                days_plan=days_plan,
                chuyen_di=chuyen_di
            )
        )

        days_plan = cost_result["days_plan"]
        cost_summary = cost_result["cost_summary"]

        return {
            "context": {
                "ten_chuyen_di": chuyen_di.ten_chuyen_di,
                "tinh_den": (
                    chuyen_di.tinh_den.ten_tinh
                    if chuyen_di.tinh_den
                    else ""
                ),
                "so_ngay": so_ngay
            },

            "summary": {
                "total_accommodations": len(accommodations),
                "total_travel_places": len(travel_places),
                "total_days": len(days_plan),
                "cost_summary": cost_summary
            },

            "days_plan": [
                {
                    "day": day["day"],

                    "accommodation": (
                        day["accommodation"]["metadata"]["ten"]
                        if day.get("accommodation")
                        else None
                    ),

                    "total_distance": day["total_distance"],
                    "cost": day["cost"],

                    "route": [
                        place["metadata"]["ten"]
                        for place in day["places"]
                    ],

                    "schedule": [
                        {
                            "place": item["place"]["metadata"]["ten"],
                            "start_time": item["start_time"],
                            "end_time": item["end_time"],
                            "travel_minutes": item["travel_minutes"],
                            "is_golden_hour": item["is_golden_hour"],
                            "valid": item["valid"]
                        }
                        for item in day.get("schedule", [])
                    ],

                    "segments": [
                        {
                            "from": segment["from"]["metadata"]["ten"],
                            "to": segment["to"]["metadata"]["ten"],
                            "distance": segment["distance"],
                            "vehicle": segment.get("vehicle_name"),
                            "vehicle_count": segment.get("vehicle_count", 0),
                            "cost": segment.get("cost", 0)
                        }
                        for segment in day.get("segments", [])
                    ]
                }
                for day in days_plan
            ],

            "cost_summary": cost_summary
        }