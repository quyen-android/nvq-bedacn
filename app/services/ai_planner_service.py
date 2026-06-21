import time

from sqlalchemy.orm import Session

from app.models.phuong_tien import PhuongTien
from app.models.chuyen_di import ChuyenDi
from app.models.dia_diem import DiaDiem

from app.core.config import settings

from app.services.gemini_service import GeminiService
from app.services.rag_service import RagService
from app.services.xep_hang_service import XepHangService
from app.services.kiem_tra_lich_trinh_service import KiemTraLichTrinhService
from app.services.sua_lich_trinh_service import SuaLichTrinhService
from app.services.toi_uu_tuyen_duong_service import ToiUuTuyenDuongService
from app.services.kiem_tra_gio_mo_cua_service import KiemTraGioMoCuaService
from app.services.du_toan_chi_phi_service import DuToanChiPhiService
from app.services.luu_lich_trinh_ai_service import LuuLichTrinhAIService
from app.services.nhat_ky_ai_service import NhatKyAIService
from app.utils.distance import haversine


class AIPlannerService:

    MAX_REPAIR_BUDGET = 3

    @staticmethod
    def sort_items_by_time(lich_trinh_json):
        for day in lich_trinh_json.get("days", []):
            items = day.get("items", [])

            def time_key(item):
                start_time = item.get("start_time")

                if start_time == "overnight":
                    return "99:99"

                return str(start_time)

            day["items"] = sorted(
                items,
                key=time_key
            )

        return lich_trinh_json

    @staticmethod
    def gan_khoang_cach_vao_items(lich_trinh_json):
        for day in lich_trinh_json.get("days", []):
            items = day.get("items", [])
            travel_segments = day.get("travel_segments", [])

            item_map = {
                str(item.get("id")): item
                for item in items
                if item.get("id")
            }

            for item in items:
                item["distance_km"] = float(
                    item.get("distance_km") or 0
                )

            for segment in travel_segments:
                to_item_id = segment.get("to_item_id")

                if not to_item_id:
                    continue

                item = item_map.get(str(to_item_id))

                if not item:
                    continue

                item["from_item_id"] = segment.get("from_item_id")
                item["from_name"] = segment.get("from_name")

                item["distance_km"] = float(
                    segment.get("distance_km") or 0
                )

                item["estimated_transport_cost"] = float(
                    segment.get("estimated_transport_cost") or 0
                )

                item["ma_pt"] = (
                    segment.get("ma_pt")
                    or item.get("ma_pt")
                )

                item["suggested_transport_name"] = (
                    segment.get("transport_name")
                    or item.get("suggested_transport_name")
                )

                item["number_of_vehicles"] = int(
                    segment.get("number_of_vehicles")
                    or item.get("number_of_vehicles")
                    or 1
                )

        return lich_trinh_json

    @staticmethod
    def save_ai_log(
        db,
        chuyen_di,
        cau_hoi,
        cau_tra_loi,
        ngu_canh,
        started_at,
        tokens_su_dung
    ):
        try:
            NhatKyAIService.tao_log(
                db=db,
                ma_nguoi_dung=chuyen_di.ma_nguoi_dung,
                ma_chuyen_di=chuyen_di.ma_chuyen_di,
                cau_hoi=cau_hoi,
                cau_tra_loi=cau_tra_loi,
                ngu_canh=ngu_canh,
                model=settings.GEMINI_MODEL,
                tokens_su_dung=tokens_su_dung,
                tg_phan_hoi=round(time.time() - started_at, 3)
            )

            db.commit()

        except Exception as e:
            db.rollback()
            print("Lỗi lưu nhật ký AI:", str(e))

    @staticmethod
    def get_phuong_tien_lien_tinh(db: Session, chuyen_di):
        ma_pt_di = getattr(
            chuyen_di,
            "ma_pt_di",
            None
        )

        ma_pt_ve = getattr(
            chuyen_di,
            "ma_pt_ve",
            None
        )

        if not ma_pt_di:
            ma_pt_di = getattr(
                chuyen_di,
                "ma_pt",
                None
            )

        if not ma_pt_ve:
            ma_pt_ve = ma_pt_di

        if not ma_pt_di:
            raise ValueError(
                "Chuyến đi chưa chọn phương tiện đi"
            )

        if not ma_pt_ve:
            raise ValueError(
                "Chuyến đi chưa chọn phương tiện về"
            )

        pt_di = (
            db.query(PhuongTien)
            .filter(PhuongTien.ma_pt == ma_pt_di)
            .first()
        )

        pt_ve = (
            db.query(PhuongTien)
            .filter(PhuongTien.ma_pt == ma_pt_ve)
            .first()
        )

        if not pt_di:
            raise ValueError(
                "Không tìm thấy phương tiện đi"
            )

        if not pt_ve:
            raise ValueError(
                "Không tìm thấy phương tiện về"
            )

        return pt_di, pt_ve

    @classmethod
    def tinh_chi_phi_lien_tinh(
        cls,
        db: Session,
        chuyen_di,
        so_nguoi
    ):
        tinh_di = chuyen_di.tinh_di
        tinh_den = chuyen_di.tinh_den

        if not tinh_di:
            raise ValueError(
                "Chuyến đi chưa có tỉnh đi"
            )

        if not tinh_den:
            raise ValueError(
                "Chuyến đi chưa có tỉnh đến"
            )

        if (
            tinh_di.vi_do is None
            or tinh_di.kinh_do is None
            or tinh_den.vi_do is None
            or tinh_den.kinh_do is None
        ):
            raise ValueError(
                "Tỉnh đi hoặc tỉnh đến chưa có tọa độ"
            )

        pt_di, pt_ve = cls.get_phuong_tien_lien_tinh(
            db=db,
            chuyen_di=chuyen_di
        )

        khoang_cach_km = haversine(
            float(tinh_di.vi_do),
            float(tinh_di.kinh_do),
            float(tinh_den.vi_do),
            float(tinh_den.kinh_do)
        )

        chi_phi_di = (
            float(khoang_cach_km)
            * float(pt_di.gia_moi_km or 0)
            * int(so_nguoi)
        )

        chi_phi_ve = (
            float(khoang_cach_km)
            * float(pt_ve.gia_moi_km or 0)
            * int(so_nguoi)
        )

        tong_chi_phi_lien_tinh = ( chi_phi_di + chi_phi_ve )

        return {
            "khoang_cach_km": round( khoang_cach_km,2 ),
                      
            "luot_di": {
                "ma_pt": str(pt_di.ma_pt),
                "ten_pt": pt_di.ten_pt,
                "gia_moi_km": float(pt_di.gia_moi_km or 0),
                "chi_phi": round(chi_phi_di, 0),
            },

            "luot_ve": {
                "ma_pt": str(pt_ve.ma_pt),
                "ten_pt": pt_ve.ten_pt,
                "gia_moi_km": float(pt_ve.gia_moi_km or 0),
                "chi_phi": round(chi_phi_ve, 0),
            },

            "tong_chi_phi_lien_tinh": round(
                tong_chi_phi_lien_tinh,
                0
            )
        }

    @classmethod
    def gan_chi_phi_lien_tinh_vao_lich_trinh(
        cls,
        lich_trinh_json,
        chi_phi_lien_tinh,
        ngan_sach_goc,
        ngan_sach_con_lai
    ):
        cost_summary = lich_trinh_json.get(
            "cost_summary",
            {}
        )

        chi_phi_noi_tinh = float(
            cost_summary.get("tong_chi_phi")
            or cost_summary.get("estimated_total_cost")
            or lich_trinh_json.get("estimated_total_cost")
        )

        tong_chi_phi_lien_tinh = float(
            chi_phi_lien_tinh.get(
                "tong_chi_phi_lien_tinh",
                0
            )
        )

        tong_chi_phi_chuyen_di = (tong_chi_phi_lien_tinh + chi_phi_noi_tinh)

        cost_summary["chi_phi_lien_tinh"] = chi_phi_lien_tinh
        cost_summary["chi_phi_noi_tinh"] = round(chi_phi_noi_tinh,0)
        cost_summary["tong_chi_phi_lien_tinh"] = round(tong_chi_phi_lien_tinh,0)
        cost_summary["tong_chi_phi_chuyen_di"] = round(tong_chi_phi_chuyen_di,0)
        cost_summary["ngan_sach_goc"] = round(float(ngan_sach_goc),0)
        cost_summary["ngan_sach_sau_khi_tru_lien_tinh"] = round(float(ngan_sach_con_lai),0)
        cost_summary["vuot_ngan_sach_tong"] = (tong_chi_phi_chuyen_di > float(ngan_sach_con_lai))
        cost_summary["so_tien_vuot_tong"] = max(0,round(tong_chi_phi_chuyen_di - float(ngan_sach_con_lai),0))
        lich_trinh_json["cost_summary"] = cost_summary
        lich_trinh_json["estimated_total_cost"] = round(tong_chi_phi_chuyen_di,0)

        return lich_trinh_json

    @classmethod
    def get_trip_info(
        cls,
        db: Session,
        ma_chuyen_di
    ):
        chuyen_di = (
            db.query(ChuyenDi)
            .filter(
                ChuyenDi.ma_chuyen_di == ma_chuyen_di
            )
            .first()
        )

        if not chuyen_di:
            raise ValueError("Không tìm thấy chuyến đi")

        tinh_di = (
            chuyen_di.tinh_di.ten_tinh
            if chuyen_di.tinh_di
            else None
        )

        tinh_den = (
            chuyen_di.tinh_den.ten_tinh
            if chuyen_di.tinh_den
            else None
        )

        if not tinh_di:
            raise ValueError("Chuyến đi chưa có tỉnh đi")

        if not tinh_den:
            raise ValueError("Chuyến đi chưa có tỉnh đến")

        if chuyen_di.ngay_di and chuyen_di.ngay_ve:
            so_ngay = (chuyen_di.ngay_ve - chuyen_di.ngay_di).days + 1

        else:
            raise ValueError("Chuyến đi chưa có ngày đi/ngày về")

        if so_ngay <= 0:
            raise ValueError("Ngày về phải lớn hơn hoặc bằng ngày đi")

        so_nguoi = chuyen_di.so_nguoi

        ngan_sach_goc = (
            float(chuyen_di.ngan_sach)
            if chuyen_di.ngan_sach
            else 0
        )

        chi_phi_lien_tinh = cls.tinh_chi_phi_lien_tinh(
            db=db,
            chuyen_di=chuyen_di,
            so_nguoi=so_nguoi
        )

        tong_chi_phi_lien_tinh = float(
            chi_phi_lien_tinh.get(
                "tong_chi_phi_lien_tinh",
                0
            )
        )

        ngan_sach_con_lai = max(0, ngan_sach_goc - tong_chi_phi_lien_tinh)
            
        cau_hoi_user = (
            f"Lên lịch trình du lịch từ {tinh_di} đến {tinh_den}. "
            f"Tên chuyến đi: {chuyen_di.ten_chuyen_di or ''}. "
            f"Số ngày: {so_ngay}. "
            f"Số người: {so_nguoi}. "
            f"Ngân sách tổng: {ngan_sach_goc}. "
            f"Chi phí liên tỉnh dự kiến: {tong_chi_phi_lien_tinh}. "
            f"Ngân sách còn lại cho ăn uống, tham quan, lưu trú và di chuyển nội tỉnh: {ngan_sach_con_lai}."
        )

        return {
            "chuyen_di": chuyen_di,
            "tinh_di": tinh_di,
            "tinh_den": tinh_den,
            "so_ngay": so_ngay,
            "so_nguoi": so_nguoi,
            "ngan_sach_goc": ngan_sach_goc,
            "ngan_sach": ngan_sach_con_lai,
            "ngan_sach_con_lai": ngan_sach_con_lai,
            "chi_phi_lien_tinh": chi_phi_lien_tinh,
            "cau_hoi_user": cau_hoi_user
        }

    @staticmethod
    def get_local_vehicles(db: Session):
        vehicles = (
            db.query(PhuongTien)
            .filter(
                PhuongTien.loai != "lien_tinh"
            )
            .all()
        )

        if not vehicles:
            raise ValueError("Không có phương tiện địa phương")

        return vehicles

    @staticmethod
    def search_and_rank_places(
        cau_hoi_user,
        tinh_den,
        so_ngay
    ):
        rag_results = RagService.search_places(
            query=cau_hoi_user,
            tinh=tinh_den,
            so_ngay=so_ngay
        )

        if not rag_results:
            raise ValueError(
                f"RAG không tìm thấy địa điểm tại {tinh_den}"
            )

        ranked_places = XepHangService.rank_places(
            rag_results
        )

        if not ranked_places:
            raise ValueError("Không có địa điểm sau khi xếp hạng")

        return ranked_places

    @staticmethod
    def get_rag_place_id(place):
        return (
            place.get("ma_dia_diem")
            or place.get("metadata", {}).get("ma_dia_diem")
        )

    @classmethod
    def get_db_places_from_rag(
        cls,
        db: Session,
        rag_places
    ):
        ids = []

        for place in rag_places:
            ma_dia_diem = cls.get_rag_place_id(place)

            if ma_dia_diem:
                ids.append(str(ma_dia_diem))

        ids = list(set(ids))

        if not ids:
            return []

        return (
            db.query(DiaDiem)
            .filter(
                DiaDiem.ma_dia_diem.in_(ids)
            )
            .all()
        )

    @classmethod
    def process_itinerary_once(
        cls,
        lich_trinh_json,
        db_places,
        vehicles,
        so_ngay,
        so_nguoi,
        ngan_sach,
        ngan_sach_goc,
        chi_phi_lien_tinh
    ):
        loi_co_ban = KiemTraLichTrinhService.kiem_tra(
            lich_trinh_ai=lich_trinh_json,
            db_places=db_places,
            db_vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi
        )

        if loi_co_ban:
            lich_trinh_json = SuaLichTrinhService.sua(
                lich_trinh_ai=lich_trinh_json,
                db_places=db_places,
                db_vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi
            )

        lich_trinh_json = cls.sort_items_by_time(
            lich_trinh_json
        )

        lich_trinh_json = ToiUuTuyenDuongService.toi_uu(
            lich_trinh_ai=lich_trinh_json,
            db_places=db_places
        )

        lich_trinh_json = cls.gan_khoang_cach_vao_items(
            lich_trinh_json
        )

        lich_trinh_json = cls.sort_items_by_time(
            lich_trinh_json
        )

        loi_gio = KiemTraGioMoCuaService.kiem_tra(
            lich_trinh_ai=lich_trinh_json,
            db_places=db_places
        )

        lich_trinh_json = DuToanChiPhiService.tinh_du_toan(
            lich_trinh_ai=lich_trinh_json,
            db_places=db_places,
            db_vehicles=vehicles,
            so_nguoi=so_nguoi,
            ngan_sach=ngan_sach
        )

        lich_trinh_json = cls.gan_khoang_cach_vao_items(
            lich_trinh_json
        )

        lich_trinh_json = cls.gan_chi_phi_lien_tinh_vao_lich_trinh(
            lich_trinh_json=lich_trinh_json,
            chi_phi_lien_tinh=chi_phi_lien_tinh,
            ngan_sach_goc=ngan_sach_goc,
            ngan_sach_con_lai=ngan_sach
        )

        cost_summary = lich_trinh_json.get("cost_summary", {})

        lich_trinh_json["validation"] = {
            "loi_co_ban": loi_co_ban,
            "loi_gio_mo_cua": loi_gio,
            "vuot_ngan_sach": cost_summary.get(
                "vuot_ngan_sach",
                False
            ),
            "vuot_ngan_sach_tong": cost_summary.get(
                "vuot_ngan_sach_tong",
                False
            )
        }

        return lich_trinh_json

    @classmethod
    def validate_before_save(cls, lich_trinh_json):
        if not isinstance(lich_trinh_json, dict):
            raise ValueError("Kết quả AI không phải JSON object")

        if "days" not in lich_trinh_json:
            raise ValueError("Lịch trình thiếu days")

        validation = lich_trinh_json.get("validation", {})

        if validation.get("loi_co_ban"):
            raise ValueError(
                "Lịch trình còn lỗi cơ bản: "
                + str(validation.get("loi_co_ban"))
            )

        if validation.get("loi_gio_mo_cua"):
            print(
                "Lịch trình còn lỗi giờ mở cửa nhưng vẫn lưu bản nháp:",
                validation.get("loi_gio_mo_cua")
            )

        cost_summary = lich_trinh_json.get("cost_summary", {})

        if cost_summary.get("vuot_ngan_sach"):
            raise ValueError(
                "Lịch trình vượt ngân sách còn lại: "
                + str(cost_summary.get("so_tien_vuot"))
            )

        if cost_summary.get("vuot_ngan_sach_tong"):
            raise ValueError("Lịch trình vượt ngân sách tổng: " + str(cost_summary.get("so_tien_vuot_tong")))
  
    @classmethod
    def generate_and_save(
        cls,
        db: Session,
        ma_chuyen_di
    ):
        request_started_at = time.time()

        trip_info = cls.get_trip_info(
            db=db,
            ma_chuyen_di=ma_chuyen_di
        )

        chuyen_di = trip_info["chuyen_di"]
        tinh_den = trip_info["tinh_den"]
        so_ngay = trip_info["so_ngay"]
        so_nguoi = trip_info["so_nguoi"]
        ngan_sach = trip_info["ngan_sach"]
        ngan_sach_goc = trip_info["ngan_sach_goc"]
        chi_phi_lien_tinh = trip_info["chi_phi_lien_tinh"]
        cau_hoi_user = trip_info["cau_hoi_user"]

        if ngan_sach <= 0:
            raise ValueError(
                "Ngân sách còn lại sau khi trừ chi phí liên tỉnh không đủ để lập lịch trình"
            )

        vehicles = cls.get_local_vehicles(db)

        rag_places = cls.search_and_rank_places(
            cau_hoi_user=cau_hoi_user,
            tinh_den=tinh_den,
            so_ngay=so_ngay
        )

        db_places = cls.get_db_places_from_rag(
            db=db,
            rag_places=rag_places
        )

        if not db_places:
            raise ValueError("Không lấy được địa điểm DB từ RAG")
        
        gemini_result = GeminiService.len_lich_trinh_sang_tao(
            cau_hoi_user=cau_hoi_user,
            places=rag_places,
            vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi,
            ngan_sach=ngan_sach
        )

        lich_trinh_json = gemini_result["itinerary"]

        tong_tokens = gemini_result["tokens_su_dung"]

        for lan_sua in range(cls.MAX_REPAIR_BUDGET + 1):
            lich_trinh_json = cls.process_itinerary_once(
                lich_trinh_json=lich_trinh_json,
                db_places=db_places,
                vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach,
                ngan_sach_goc=ngan_sach_goc,
                chi_phi_lien_tinh=chi_phi_lien_tinh
            )

            cost_summary = lich_trinh_json.get(
                "cost_summary",
                {}
            )

            if not cost_summary.get("vuot_ngan_sach"):
                break

            if lan_sua >= cls.MAX_REPAIR_BUDGET:
                break

            repair_result = GeminiService.sua_lich_trinh_theo_ngan_sach(
                lich_trinh_ai=lich_trinh_json,
                cost_summary=cost_summary,
                cau_hoi_user=cau_hoi_user,
                places=rag_places,
                vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach
            )

            lich_trinh_json = repair_result["itinerary"]

            tong_tokens += repair_result["tokens_su_dung"]

        lich_trinh_json = cls.gan_khoang_cach_vao_items(
            lich_trinh_json
        )

        cls.validate_before_save(
            lich_trinh_json
        )

        save_result = LuuLichTrinhAIService.luu(
            db=db,
            chuyen_di=chuyen_di,
            lich_trinh_ai=lich_trinh_json
        )

        answer_log = (
            "Tạo lịch trình AI thành công. "
            f"Chi phí liên tỉnh: {chi_phi_lien_tinh.get('tong_chi_phi_lien_tinh')}. "
            f"Tổng chi phí chuyến đi: {lich_trinh_json.get('estimated_total_cost')}. "
            f"{lich_trinh_json.get('budget_note', '')}"
        )

        cls.save_ai_log(
            db=db,
            chuyen_di=chuyen_di,
            cau_hoi=cau_hoi_user,
            cau_tra_loi=answer_log,
            ngu_canh="tao_lich_trinh_ai",
            started_at=request_started_at,
            tokens_su_dung=tong_tokens
        )

        return {
            "message": "Tạo lịch trình AI thành công",
            "chi_phi_lien_tinh": chi_phi_lien_tinh,
            "ngan_sach_goc": ngan_sach_goc,
            "ngan_sach_con_lai": ngan_sach,
            "save_result": save_result,
            "itinerary": lich_trinh_json
        }