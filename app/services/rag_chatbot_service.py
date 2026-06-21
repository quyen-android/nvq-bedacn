import json
import re
import time

from sqlalchemy.orm import Session

from app.models.chuyen_di import ChuyenDi
from app.models.lich_trinh import LichTrinh
from app.models.chi_tiet_lich_trinh import ChiTietLichTrinh
from app.models.dia_diem import DiaDiem
from app.models.phuong_tien import PhuongTien

from app.services.rag_service import RagService
from app.services.gemini_service import GeminiService
from app.services.nhat_ky_ai_service import NhatKyAIService
from app.core.config import settings


class RagChatbotService:

    @staticmethod
    def normalize_text(value):
        if not value:
            return ""

        return str(value).strip().lower()

    @staticmethod
    def safe_str(value):
        return str(value) if value else None

    @staticmethod
    def get_chi_tiet_id(ct):
        value = (
            getattr(ct, "ma_chi_tiet", None)
            or getattr(ct, "ma_chi_tiet_lich_trinh", None)
            or getattr(ct, "ma_ctlt", None)
            or getattr(ct, "id", None)
        )

        return str(value) if value else None

    @staticmethod
    def check_trip_owner(
        db: Session,
        ma_chuyen_di,
        current_user
    ):
        chuyen_di = (
            db.query(ChuyenDi)
            .filter(
                ChuyenDi.ma_chuyen_di == ma_chuyen_di,
                ChuyenDi.ma_nguoi_dung == current_user.ma_nguoi_dung
            )
            .first()
        )

        if not chuyen_di:
            raise ValueError("Không tìm thấy chuyến đi")

        return chuyen_di

    @staticmethod
    def save_ai_log(
        db,
        current_user,
        ma_chuyen_di,
        message,
        answer,
        context,
        started_at,
        tokens_su_dung=None
    ):
        try:
            NhatKyAIService.tao_log(
                db=db,
                ma_nguoi_dung=current_user.ma_nguoi_dung,
                ma_chuyen_di=ma_chuyen_di,
                cau_hoi=message,
                cau_tra_loi=answer,
                ngu_canh=context,
                model=settings.GEMINI_MODEL,
                tokens_su_dung=tokens_su_dung,
                tg_phan_hoi=round(time.time() - started_at, 3)
            )

            db.commit()

        except Exception as e:
            db.rollback()
            print("Lỗi lưu nhật ký AI:", str(e))

    @classmethod
    def detect_action(cls, message):
        text = cls.normalize_text(message)

        if (
            "đổi" in text
            or "thay " in text
            or "thay thế" in text
        ):
            return "replace"

        if (
            "xóa" in text
            or "bỏ" in text
            or "loại bỏ" in text
        ):
            return "delete"

        if (
            "thêm" in text
            or "add" in text
            or "bổ sung" in text
        ):
            return "add"

        return "chat"

    @classmethod
    def extract_day_number(cls, message):
        text = cls.normalize_text(message)

        match = re.search(r"ngày\s+(\d+)", text)

        if match:
            return int(match.group(1))

        match = re.search(r"day\s+(\d+)", text)

        if match:
            return int(match.group(1))

        return None

    @classmethod
    def extract_time_range(cls, message):
        text = cls.normalize_text(message)

        match = re.search(
            r"(\d{1,2}:\d{2})\s*(?:-|đến|to)\s*(\d{1,2}:\d{2})",
            text
        )

        if match:
            return match.group(1), match.group(2)

        match = re.search(
            r"lúc\s+(\d{1,2}:\d{2})",
            text
        )

        if match:
            return match.group(1), None

        return None, None

    @classmethod
    def extract_delete_place_name(cls, message):
        raw = str(message or "").strip()

        text = re.sub(
            r"(?i)\b(xóa|xoá|bỏ|loại bỏ)\b",
            "",
            raw
        )

        text = re.sub(
            r"(?i)\b(khỏi|trong|ở|vào)?\s*ngày\s+\d+\b",
            "",
            text
        )

        text = text.strip(" .,-:")

        return text or None

    @classmethod
    def extract_add_place_name(cls, message):
        raw = str(message or "").strip()

        text = re.sub(
            r"(?i)\b(thêm|add|bổ sung)\b",
            "",
            raw
        )

        text = re.sub(
            r"(?i)\b(vào|ở|trong)?\s*ngày\s+\d+\b",
            "",
            text
        )

        text = re.sub(
            r"(?i)\blúc\s+\d{1,2}:\d{2}\b",
            "",
            text
        )

        text = re.sub(
            r"\d{1,2}:\d{2}\s*(?:-|đến|to)\s*\d{1,2}:\d{2}",
            "",
            text
        )

        text = text.strip(" .,-:")

        return text or None

    @classmethod
    def extract_replace_place_names(cls, message):
        raw = str(message or "").strip()

        match = re.search(
            r"(?i)(?:đổi|thay|thay thế)\s+(.+?)\s+(?:thành|bằng)\s+(.+)",
            raw
        )

        if not match:
            return None, None

        old_name = match.group(1)
        new_name = match.group(2)

        old_name = re.sub(
            r"(?i)\bngày\s+\d+\b",
            "",
            old_name
        ).strip(" .,-:")

        new_name = re.sub(
            r"(?i)\bngày\s+\d+\b",
            "",
            new_name
        ).strip(" .,-:")

        new_name = re.sub(
            r"(?i)\blúc\s+\d{1,2}:\d{2}\b",
            "",
            new_name
        ).strip(" .,-:")

        new_name = re.sub(
            r"\d{1,2}:\d{2}\s*(?:-|đến|to)\s*\d{1,2}:\d{2}",
            "",
            new_name
        ).strip(" .,-:")

        return old_name or None, new_name or None

    @classmethod
    def build_itinerary_update_from_db(
        cls,
        db: Session,
        chuyen_di
    ):
        lich_trinhs = (
            db.query(LichTrinh)
            .filter(
                LichTrinh.ma_chuyen_di == chuyen_di.ma_chuyen_di
            )
            .order_by(LichTrinh.ngay.asc())
            .all()
        )

        days = []

        for index, lich_trinh in enumerate(lich_trinhs, start=1):
            chi_tiets = (
                db.query(ChiTietLichTrinh)
                .filter(
                    ChiTietLichTrinh.ma_lich_trinh
                    == lich_trinh.ma_lich_trinh
                )
                .order_by(ChiTietLichTrinh.gio_bat_dau.asc())
                .all()
            )

            items = []

            for ct in chi_tiets:
                items.append({
                    "ma_chi_tiet": cls.get_chi_tiet_id(ct),
                    "ma_dia_diem": cls.safe_str(ct.ma_dia_diem),
                    "start_time": (
                        ct.gio_bat_dau.strftime("%H:%M")
                        if ct.gio_bat_dau
                        else None
                    ),
                    "end_time": (
                        ct.gio_ket_thuc.strftime("%H:%M")
                        if ct.gio_ket_thuc
                        else None
                    ),
                    "ma_pt": cls.safe_str(ct.ma_pt),
                    "distance_km": float(ct.khoang_cach or 0),
                    "number_of_vehicles": ct.so_luong_pt or 1,
                    "estimated_transport_cost": float(ct.gia or 0),
                })

            days.append({
                "day": index,
                "items": items
            })

        return {
            "days": days
        }

    @classmethod
    def find_day(cls, itinerary_update, day_number):
        if not day_number:
            raise ValueError("Bạn cần nói rõ muốn sửa ngày mấy")

        for day in itinerary_update.get("days", []):
            if int(day.get("day") or 0) == int(day_number):
                return day

        raise ValueError(f"Không tìm thấy ngày {day_number}")

    @classmethod
    def get_place_by_id(cls, db, ma_dia_diem):
        if not ma_dia_diem:
            return None

        return (
            db.query(DiaDiem)
            .filter(DiaDiem.ma_dia_diem == ma_dia_diem)
            .first()
        )

    @classmethod
    def get_place_name_by_id(cls, db, ma_dia_diem):
        place = cls.get_place_by_id(
            db,
            ma_dia_diem
        )

        return place.ten if place else ""

    @classmethod
    def find_item_index_by_place_name(
        cls,
        db,
        items,
        place_name
    ):
        target = cls.normalize_text(place_name)

        if not target:
            return None

        for index, item in enumerate(items):
            current_name = cls.get_place_name_by_id(
                db,
                item.get("ma_dia_diem")
            )

            if target in cls.normalize_text(current_name):
                return index

        return None

    @classmethod
    def find_place_by_rag(
        cls,
        db,
        query,
        tinh_den
    ):
        if not query:
            raise ValueError("Bạn cần nói rõ tên địa điểm")

        rag_results = RagService.search_places(
            query=query,
            tinh=tinh_den,
            so_ngay=3
        )

        if not rag_results:
            raise ValueError(
                f"Không tìm thấy địa điểm phù hợp với '{query}'"
            )

        first = rag_results[0]
        metadata = first.get("metadata", {})

        ma_dia_diem = (
            first.get("ma_dia_diem")
            or metadata.get("ma_dia_diem")
        )

        if not ma_dia_diem:
            raise ValueError("RAG không trả về mã địa điểm")

        dia_diem = (
            db.query(DiaDiem)
            .filter(DiaDiem.ma_dia_diem == ma_dia_diem)
            .first()
        )

        if not dia_diem:
            raise ValueError(
                f"Không tìm thấy địa điểm '{query}' trong DB"
            )

        return dia_diem

    @staticmethod
    def get_default_vehicle_id(chuyen_di):
        if getattr(chuyen_di, "ma_pt", None):
            return str(chuyen_di.ma_pt)

        if getattr(chuyen_di, "ma_pt_di", None):
            return str(chuyen_di.ma_pt_di)

        return None

    @classmethod
    def ai_suggest_time_for_place(
        cls,
        message,
        day_number,
        place_name,
        current_day_items
    ):
        current_schedule = []

        for item in current_day_items:
            current_schedule.append({
                "start_time": item.get("start_time"),
                "end_time": item.get("end_time"),
                "ma_dia_diem": item.get("ma_dia_diem")
            })

        prompt = f"""
            Bạn là AI lập lịch du lịch.

            Hãy chọn giờ bắt đầu và giờ kết thúc phù hợp cho địa điểm mới.

            Yêu cầu:
            - Không trùng với các khung giờ hiện có.
            - Không fix cứng giờ.
            - Ưu tiên khoảng trống hợp lý trong ngày.
            - Ưu tiên tối ưu hóa đường đi.
            - Nếu người dùng có nói giờ thì ưu tiên giờ người dùng.
            - Chỉ trả về JSON hợp lệ, không giải thích.

            Câu yêu cầu của người dùng:
            {message}

            Ngày cần sửa:
            {day_number}

            Địa điểm cần thêm/đổi:
            {place_name}

            Lịch hiện tại trong ngày:
            {current_schedule}

            Format trả về:
            {{
            "start_time": "HH:MM",
            "end_time": "HH:MM"
            }}
            """

        try:
            result = GeminiService.chat_text_with_usage(prompt)

            text = str(result.get("text", "")).strip()
            tokens = result.get("tokens_su_dung", 0)

            if text.startswith("```"):
                text = text.replace("```json", "")
                text = text.replace("```", "")
                text = text.strip()

            data = json.loads(text)

            suggested_start_time = data.get("start_time")
            suggested_end_time = data.get("end_time")

            if suggested_start_time and suggested_end_time:
                return suggested_start_time, suggested_end_time,tokens

            return None, None, tokens

        except Exception as e:
            print("AI TIME ERROR:", e)
            return None, None, 0

    @classmethod
    def resolve_time_for_action(
        cls,
        message,
        day_number,
        place_name,
        target_day
    ):
        parsed_start_time, parsed_end_time = cls.extract_time_range(
            message
        )

        if parsed_start_time and parsed_end_time:
            return parsed_start_time, parsed_end_time

        ai_start_time, ai_end_time, ai_tokens = cls.ai_suggest_time_for_place(
            message=message,
            day_number=day_number,
            place_name=place_name,
            current_day_items=target_day.get("items", [])
        )

        final_start_time = parsed_start_time or ai_start_time
        final_end_time = parsed_end_time or ai_end_time

        if not final_start_time or not final_end_time:
            raise ValueError(
                "AI chưa chọn được giờ phù hợp. "
                "Bạn hãy nói rõ giờ, ví dụ: thêm Biển Mỹ Khê vào ngày 2 lúc 15:00"
            )

        return final_start_time, final_end_time, ai_tokens

    @classmethod
    def create_item_from_place(
        cls,
        dia_diem,
        chuyen_di,
        start_time,
        end_time,
        old_item=None
    ):
        ma_pt = None

        if old_item:
            ma_pt = old_item.get("ma_pt")

        if not ma_pt:
            ma_pt = cls.get_default_vehicle_id(chuyen_di)

        number_of_vehicles = 1

        if old_item:
            number_of_vehicles = (
                old_item.get("number_of_vehicles")
                or 1
            )

        return {
            "ma_chi_tiet": None,
            "ma_dia_diem": str(dia_diem.ma_dia_diem),
            "start_time": start_time,
            "end_time": end_time,
            "ma_pt": ma_pt,
            "distance_km": 0,
            "number_of_vehicles": number_of_vehicles,
            "estimated_transport_cost": 0,
        }

    @classmethod
    def delete_place_from_day(
        cls,
        db,
        itinerary_update,
        day_number,
        place_name
    ):
        target_day = cls.find_day(
            itinerary_update,
            day_number
        )

        index = cls.find_item_index_by_place_name(
            db=db,
            items=target_day.get("items", []),
            place_name=place_name
        )

        if index is None:
            raise ValueError(
                f"Không tìm thấy địa điểm '{place_name}' trong ngày {day_number}"
            )

        deleted_item = target_day["items"].pop(index)

        deleted_name = cls.get_place_name_by_id(
            db,
            deleted_item.get("ma_dia_diem")
        )

        return deleted_name

    @classmethod
    def add_place_to_day(
        cls,
        itinerary_update,
        day_number,
        new_item
    ):
        target_day = cls.find_day(
            itinerary_update,
            day_number
        )

        target_day.setdefault("items", [])
        target_day["items"].append(new_item)

    @classmethod
    def replace_place_in_day(
        cls,
        db,
        itinerary_update,
        day_number,
        old_place_name,
        new_item
    ):
        target_day = cls.find_day(
            itinerary_update,
            day_number
        )

        index = cls.find_item_index_by_place_name(
            db=db,
            items=target_day.get("items", []),
            place_name=old_place_name
        )

        if index is None:
            raise ValueError(
                f"Không tìm thấy địa điểm '{old_place_name}' trong ngày {day_number}"
            )

        old_item = target_day["items"][index]

        if not new_item.get("ma_pt"):
            new_item["ma_pt"] = old_item.get("ma_pt")

        if not new_item.get("number_of_vehicles"):
            new_item["number_of_vehicles"] = (
                old_item.get("number_of_vehicles")
                or 1
            )

        target_day["items"][index] = new_item

        old_name = cls.get_place_name_by_id(
            db,
            old_item.get("ma_dia_diem")
        )

        return old_name

    @staticmethod
    def build_trip_context(
        db: Session,
        chuyen_di
    ):
        lich_trinhs = (
            db.query(LichTrinh)
            .filter(
                LichTrinh.ma_chuyen_di == chuyen_di.ma_chuyen_di
            )
            .order_by(LichTrinh.ngay.asc())
            .all()
        )

        lines = []

        lines.append("THÔNG TIN CHUYẾN ĐI:")
        lines.append(f"Tên chuyến đi: {chuyen_di.ten_chuyen_di}")
        lines.append(f"Ngày đi: {chuyen_di.ngay_di}")
        lines.append(f"Ngày về: {chuyen_di.ngay_ve}")
        lines.append(f"Số người: {chuyen_di.so_nguoi}")
        lines.append(f"Ngân sách: {chuyen_di.ngan_sach}")
        lines.append("")

        lines.append("LỊCH TRÌNH HIỆN TẠI:")

        for index, lich_trinh in enumerate(lich_trinhs, start=1):
            lines.append(f"Ngày {index} - {lich_trinh.ngay}:")

            chi_tiets = (
                db.query(ChiTietLichTrinh)
                .filter(
                    ChiTietLichTrinh.ma_lich_trinh
                    == lich_trinh.ma_lich_trinh
                )
                .order_by(ChiTietLichTrinh.gio_bat_dau.asc())
                .all()
            )

            for ct in chi_tiets:
                dia_diem = None
                phuong_tien = None

                if ct.ma_dia_diem:
                    dia_diem = (
                        db.query(DiaDiem)
                        .filter(DiaDiem.ma_dia_diem == ct.ma_dia_diem)
                        .first()
                    )

                if ct.ma_pt:
                    phuong_tien = (
                        db.query(PhuongTien)
                        .filter(PhuongTien.ma_pt == ct.ma_pt)
                        .first()
                    )

                ten_dia_diem = (
                    dia_diem.ten
                    if dia_diem
                    else "Không rõ địa điểm"
                )

                ten_pt = (
                    phuong_tien.ten_pt
                    if phuong_tien
                    else "Chưa có phương tiện"
                )

                gio_bat_dau = (
                    ct.gio_bat_dau.strftime("%H:%M")
                    if ct.gio_bat_dau
                    else "?"
                )

                gio_ket_thuc = (
                    ct.gio_ket_thuc.strftime("%H:%M")
                    if ct.gio_ket_thuc
                    else "?"
                )

                lines.append(
                    f"- {gio_bat_dau} - {gio_ket_thuc}: "
                    f"{ten_dia_diem} | PT: {ten_pt}"
                )

            lines.append("")

        return "\n".join(lines)

    @staticmethod
    def build_rag_context(
        user_message,
        tinh_den
    ):
        rag_results = RagService.search_places(
            query=user_message,
            tinh=tinh_den,
            so_ngay=3
        )

        if not rag_results:
            return "Không tìm thấy địa điểm phù hợp từ RAG."

        lines = []
        lines.append("ĐỊA ĐIỂM RAG GỢI Ý:")

        for index, place in enumerate(rag_results[:8], start=1):
            metadata = place.get("metadata", {})

            lines.append(
                f"{index}. "
                f"{metadata.get('ten')} | "
                f"Loại: {metadata.get('loai')} | "
                f"Địa chỉ: {metadata.get('dia_chi')} | "
                f"Giá: {metadata.get('gia')} | "
                f"Đánh giá: {metadata.get('danh_gia')} | "
                f"Địa chỉ: {metadata.get('dia_chi')} | "
                f"Khung giờ vàng: {metadata.get('golden_hours')} | "
                f"ID: {metadata.get('ma_dia_diem')}"
            )

        return "\n".join(lines)

    @classmethod
    def chat(
        cls,
        db: Session,
        ma_chuyen_di,
        message,
        current_user
    ):
        if not message or not message.strip():
            raise ValueError("Tin nhắn không được để trống")

        request_started_at = time.time()

        chuyen_di = cls.check_trip_owner(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            current_user=current_user
        )

        tinh_den = (
            chuyen_di.tinh_den.ten_tinh
            if chuyen_di.tinh_den
            else ""
        )

        action = cls.detect_action(message)
        day_number = cls.extract_day_number(message)

        if action in ["delete", "add", "replace"]:
            itinerary_update = cls.build_itinerary_update_from_db(
                db=db,
                chuyen_di=chuyen_di
            )

            if action == "delete":
                place_name = cls.extract_delete_place_name(message)

                deleted_name = cls.delete_place_from_day(
                    db=db,
                    itinerary_update=itinerary_update,
                    day_number=day_number,
                    place_name=place_name
                )

                answer = (
                    f"Mình đã tạo đề xuất xóa "
                    f"'{deleted_name}' khỏi ngày {day_number}. "
                    f"Bạn hãy bấm 'Áp dụng thay đổi' để lưu vào lịch trình."
                )

                cls.save_ai_log(
                    db=db,
                    current_user=current_user,
                    ma_chuyen_di=ma_chuyen_di,
                    message=message,
                    answer=answer,
                    context="chatbot_rag_xoa_dia_diem",
                    started_at=request_started_at,
                )

                return {
                    "answer": answer,
                    "itinerary_update": itinerary_update
                }

            if action == "add":
                place_name = cls.extract_add_place_name(message)

                dia_diem = cls.find_place_by_rag(
                    db=db,
                    query=place_name,
                    tinh_den=tinh_den
                )

                target_day = cls.find_day(
                    itinerary_update,
                    day_number
                )

                item_start_time, item_end_time, tokens_su_dung  = cls.resolve_time_for_action(
                    message=message,
                    day_number=day_number,
                    place_name=dia_diem.ten,
                    target_day=target_day
                )

                new_item = cls.create_item_from_place(
                    dia_diem=dia_diem,
                    chuyen_di=chuyen_di,
                    start_time=item_start_time,
                    end_time=item_end_time
                )

                cls.add_place_to_day(
                    itinerary_update=itinerary_update,
                    day_number=day_number,
                    new_item=new_item
                )

                answer = (
                    f"Mình đã tạo đề xuất thêm "
                    f"'{dia_diem.ten}' vào ngày {day_number} "
                    f"từ {item_start_time} đến {item_end_time}. "
                    f"Bạn hãy bấm 'Áp dụng thay đổi' để lưu vào lịch trình."
                )

                cls.save_ai_log(
                    db=db,
                    current_user=current_user,
                    ma_chuyen_di=ma_chuyen_di,
                    message=message,
                    answer=answer,
                    context="chatbot_rag_them_dia_diem",
                    started_at=request_started_at,
                    tokens_su_dung=tokens_su_dung
                )

                return {
                    "answer": answer,
                    "itinerary_update": itinerary_update
                }

            if action == "replace":
                old_name, new_name = cls.extract_replace_place_names(
                    message
                )

                if not old_name or not new_name:
                    raise ValueError(
                        "Bạn hãy nói rõ theo mẫu: "
                        "'đổi Cầu Rồng ngày 1 thành Biển Mỹ Khê'"
                    )

                dia_diem_moi = cls.find_place_by_rag(
                    db=db,
                    query=new_name,
                    tinh_den=tinh_den
                )

                target_day = cls.find_day(
                    itinerary_update,
                    day_number
                )

                old_index = cls.find_item_index_by_place_name(
                    db=db,
                    items=target_day.get("items", []),
                    place_name=old_name
                )

                old_item = None

                if old_index is not None:
                    old_item = target_day.get("items", [])[old_index]

                item_start_time, item_end_time, tokens_su_dung  = cls.resolve_time_for_action(
                    message=message,
                    day_number=day_number,
                    place_name=dia_diem_moi.ten,
                    target_day=target_day
                )

                new_item = cls.create_item_from_place(
                    dia_diem=dia_diem_moi,
                    chuyen_di=chuyen_di,
                    start_time=item_start_time,
                    end_time=item_end_time,
                    old_item=old_item
                )

                old_place_real_name = cls.replace_place_in_day(
                    db=db,
                    itinerary_update=itinerary_update,
                    day_number=day_number,
                    old_place_name=old_name,
                    new_item=new_item
                )

                answer = (
                    f"Mình đã tạo đề xuất đổi "
                    f"'{old_place_real_name}' thành "
                    f"'{dia_diem_moi.ten}' ở ngày {day_number} "
                    f"từ {item_start_time} đến {item_end_time}. "
                    f"Bạn hãy bấm 'Áp dụng thay đổi' để lưu vào lịch trình."
                )
                
                # tokens_su_dung = max(
                #     1,
                #     int((len(message) + len(answer)) / 4)
                # )

                cls.save_ai_log(
                    db=db,
                    current_user=current_user,
                    ma_chuyen_di=ma_chuyen_di,
                    message=message,
                    answer=answer,
                    context="chatbot_rag_doi_dia_diem",
                    started_at=request_started_at,
                    tokens_su_dung=tokens_su_dung
                )

                return {
                    "answer": answer,
                    "itinerary_update": itinerary_update
                }

        trip_context = cls.build_trip_context(
            db=db,
            chuyen_di=chuyen_di
        )

        rag_context = cls.build_rag_context(
            user_message=message,
            tinh_den=tinh_den
        )

        prompt = f"""
            Bạn là trợ lý AI du lịch cho hệ thống TripAI.

            Nhiệm vụ:
            - Trả lời câu hỏi của người dùng dựa trên lịch trình hiện tại.
            - Nếu người dùng muốn chỉnh lịch trình, hãy hướng dẫn họ dùng một trong các mẫu:
            1. xóa Cầu Rồng ngày 1
            2. thêm Biển Mỹ Khê vào ngày 2
            3. thêm Biển Mỹ Khê vào ngày 2 lúc 15:00
            4. đổi Cầu Rồng ngày 1 thành Biển Mỹ Khê
            - Không tự ý lưu DB.
            - Trả lời ngắn gọn, dễ hiểu bằng tiếng Việt.

            {trip_context}

            {rag_context}

            CÂU HỎI NGƯỜI DÙNG:
            {message}
            """

        gemini_result = GeminiService.chat_text_with_usage(prompt)

        answer = gemini_result["text"]
        tokens_su_dung = gemini_result["tokens_su_dung"]

        cls.save_ai_log(
            db=db,
            current_user=current_user,
            ma_chuyen_di=ma_chuyen_di,
            message=message,
            answer=answer,
            context="chatbot_rag_hoi_dap",
            started_at=request_started_at,
            tokens_su_dung=tokens_su_dung
        )

        return {
            "answer": answer,
            "itinerary_update": None
        }