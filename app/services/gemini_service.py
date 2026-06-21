import json
import math

from google import genai
from google.genai import types

from app.core.config import settings


class GeminiService:
    MODEL = settings.GEMINI_MODEL

    client = genai.Client(
        api_key=settings.GEMINI_API_KEY
    )

    ACCOMMODATION_TYPE = "chỗ ở"

    @classmethod
    def chat_text(cls, prompt: str):
        response = cls.client.models.generate_content(
            model=cls.MODEL,
            contents=prompt
        )

        return response.text

    @classmethod
    def chat_text_with_usage(cls, prompt):
        response = cls.client.models.generate_content(
            model=cls.MODEL,
            contents=prompt
        )

        text = response.text or ""

        usage = getattr(
            response,
            "usage_metadata",
            None
        )

        tokens_su_dung = None

        if usage:
            prompt_tokens = (
                getattr(
                    usage,
                    "prompt_token_count",
                    0
                ) or 0
            )

            output_tokens = (
                getattr(
                    usage,
                    "candidates_token_count",
                    0
                ) or 0
            )

            total_tokens = (
                getattr(
                    usage,
                    "total_token_count",
                    0
                ) or 0
            )

            tokens_su_dung = (
                total_tokens
                or prompt_tokens + output_tokens
            )


        return {
            "text": text,
            "tokens_su_dung": tokens_su_dung
        }
    
    @staticmethod
    def safe_json_loads(value, default=None):
        if default is None:
            default = []

        if not value:
            return default

        try:
            if isinstance(value, str):
                return json.loads(value)

            return value
        except Exception:
            return default

    @classmethod
    def is_accommodation(cls, place):
        metadata = place.get("metadata", {})
        loai = str(
            metadata.get("loai", "")
        ).strip().lower()

        return loai == cls.ACCOMMODATION_TYPE

    @classmethod
    def split_accommodations_and_places(cls, places):
        accommodations = []
        travel_places = []

        for place in places:
            if cls.is_accommodation(place):
                accommodations.append(place)
            else:
                travel_places.append(place)

        return accommodations, travel_places

    @staticmethod
    def format_golden_hours(value):
        golden_hours = GeminiService.safe_json_loads(
            value,
            []
        )

        if not golden_hours:
            return "Không có"

        return "; ".join([
            f"{item.get('start')} - {item.get('end')} "
            f"(tháng {item.get('month_start')} đến {item.get('month_end')})"
            for item in golden_hours
        ])

    @classmethod
    def build_places_prompt(cls, places):
        lines = []

        for place in places:
            metadata = place.get("metadata", {})
            ranking = place.get("ranking", {})

            lines.append(
                f"- ID: {place.get('ma_dia_diem') or metadata.get('ma_dia_diem')} | "
                f"Tên: {metadata.get('ten')} | "
                f"Loại: {metadata.get('loai')} | "
                f"Tỉnh: {metadata.get('tinh')} | "
                f"Lat: {metadata.get('lat', 0)} | "
                f"Lon: {metadata.get('lon', 0)} | "
                f"Giá trung bình: {metadata.get('gia', 0)} VNĐ | "
                f"Rating: {metadata.get('danh_gia', 0)} | "
                f"Reviews: {metadata.get('so_danh_gia', 0)} | "
                f"Giờ: {metadata.get('gio_mo', '')}-{metadata.get('gio_dong', '')} | "
                f"Khung giờ vàng: {cls.format_golden_hours(metadata.get('golden_hours'))} | "
                f"Điểm phù hợp: {ranking.get('final_score', 0)}"
            )

        return "\n".join(lines)

    @staticmethod
    def build_vehicles_prompt(vehicles, so_nguoi):
        lines = []

        for vehicle in vehicles:
            suc_chua = int(vehicle.suc_chua or 1)

            so_xe_goi_y = math.ceil(
                int(so_nguoi or 1) / suc_chua
            )

            lines.append(
                f"- ID: {vehicle.ma_pt} | "
                f"Tên: {vehicle.ten_pt} | "
                f"Loại: {vehicle.loai} | "
                f"Tốc độ: {vehicle.toc_do_tb} km/h | "
                f"Giá/km: {vehicle.gia_moi_km} VNĐ | "
                f"Sức chứa/xe: {suc_chua} người | "
                f"Số xe tối thiểu cho đoàn: {so_xe_goi_y}"
            )

        return "\n".join(lines)

    @staticmethod
    def build_budget_prompt(
        ngan_sach,
        so_nguoi,
        so_ngay
    ):
        try:
            ngan_sach = float(ngan_sach or 0)
            so_nguoi = int(so_nguoi or 1)
            so_ngay = int(so_ngay or 1)
        except Exception:
            ngan_sach = 0
            so_nguoi = 1
            so_ngay = 1

        if ngan_sach <= 0:
            return """
Ngân sách: Không giới hạn rõ ràng.
Ưu tiên chọn địa điểm phù hợp nhất nhưng vẫn hợp lý.
"""

        return f"""
Tổng ngân sách chuyến đi: {round(ngan_sach)} VNĐ
Số người: {so_nguoi}
Số ngày: {so_ngay}
Ngân sách trung bình mỗi ngày: {round(ngan_sach / so_ngay)} VNĐ
Ngân sách trung bình mỗi người mỗi ngày: {round(ngan_sach / so_nguoi / so_ngay)} VNĐ
"""

    @staticmethod
    def clean_json_response(raw_response):
        cleaned = (
            raw_response
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        return json.loads(cleaned)

    @classmethod
    def build_prompt(
        cls,
        cau_hoi_user,
        accommodations,
        travel_places,
        vehicles,
        so_ngay,
        so_nguoi,
        ngan_sach
    ):
        accommodations_prompt = cls.build_places_prompt(
            accommodations
        )

        travel_places_prompt = cls.build_places_prompt(
            travel_places
        )

        vehicles_prompt = cls.build_vehicles_prompt(
            vehicles,
            so_nguoi
        )

        budget_prompt = cls.build_budget_prompt(
            ngan_sach=ngan_sach,
            so_nguoi=so_nguoi,
            so_ngay=so_ngay
        )

        return f"""
Bạn là AI Travel Planner chuyên thiết kế lịch trình du lịch Việt Nam.

NHIỆM VỤ:
- Lập lịch trình đúng {so_ngay} ngày.
- Chỉ sử dụng ID địa điểm được cung cấp.
- Chỉ sử dụng ID chỗ ở được cung cấp.
- Chỉ sử dụng ID phương tiện được cung cấp.
- Không tự tạo địa điểm mới.
- Không tự tạo phương tiện mới.
- Không chọn địa điểm đi chơi trùng lặp.
- Mỗi ngày bắt buộc có đúng 1 chỗ ở.
- Chỗ ở phải lấy từ DANH SÁCH CHỖ Ở.
- Chỗ ở phải là item cuối cùng trong ngày.
- Địa điểm đi chơi, ăn uống phải lấy từ DANH SÁCH ĐỊA ĐIỂM ĐI CHƠI / ĂN UỐNG.
- Không dùng quán ăn hoặc điểm tham quan làm chỗ ở.
- Ưu tiên địa điểm có điểm phù hợp cao.
- Ưu tiên địa điểm gần nhau dựa trên tọa độ GPS.
- Không xếp lịch quá dày.
- Có thời gian nghỉ hợp lý.
- Không vượt ngân sách nếu có thể.

QUY TẮC CHỐNG ĐI LÒNG VÒNG:
- Trong cùng một ngày, chỉ chọn các địa điểm gần nhau.
- Ưu tiên địa điểm gần nhau theo tọa độ GPS.
- Không xếp lịch kiểu: Bắc → Nam → Bắc → Nam.
- Chỗ ở cuối ngày nên gần địa điểm cuối cùng trong ngày.
- Nếu có nhiều địa điểm cùng loại gần nhau, ưu tiên địa điểm có điểm phù hợp cao hơn.
- Thứ tự trong ngày nên đi theo tuyến gần nhau, không nhảy xa liên tục.

QUY TẮC CHỖ Ở:
- Mỗi ngày bắt buộc có đúng 1 item type = "accommodation".
- Item type = "accommodation" là nơi ngủ qua đêm của ngày đó.
- Item type = "accommodation" phải là item cuối cùng trong danh sách items của ngày.
- Item type = "accommodation" phải lấy từ DANH SÁCH CHỖ Ở.
- Chỗ ở vẫn phải có start_time, time_slot, ma_pt, suggested_transport_name, number_of_vehicles.
- Với chỗ ở:
  - start_time nên là buổi tối.
  - end_time dùng giá trị "overnight".
  - time_slot = "evening".
- Chỗ ở được tính vào tuyến đường cuối ngày để backend tính chi phí di chuyển đến chỗ ở.

QUY TẮC KHUNG GIỜ VÀNG:
- Nếu địa điểm có khung giờ vàng, hãy ưu tiên start_time nằm trong khung giờ vàng.
- Nếu start_time nằm trong khung giờ vàng thì is_golden_hour_used = true.
- Nếu không thể xếp vào khung giờ vàng thì is_golden_hour_used = false.
- Luôn ghi rõ golden_hour_note.
- Với chỗ ở thì is_golden_hour_used = false và golden_hour_note = "Không áp dụng cho chỗ ở".

QUY TẮC GIỜ MỞ CỬA:
- Không xếp địa điểm ngoài giờ mở cửa.
- Với type = "place": start_time và end_time phải nằm trong giờ mở cửa - giờ đóng cửa.
- end_time phải sau start_time.
- start_time và end_time dạng HH:MM.
- Với type = "accommodation": end_time = "overnight".

QUY TẮC PHƯƠNG TIỆN:
- Mỗi item trong lịch trình phải có ma_pt.
- ma_pt là phương tiện được sử dụng để đi đến item đó.
- ma_pt phải nằm trong danh sách phương tiện được cung cấp.
- suggested_transport_name phải đúng tên phương tiện tương ứng với ma_pt.
- Không được sử dụng phương tiện liên tỉnh cho việc di chuyển giữa các item trong lịch trình.
- Không được chọn phương tiện có sức chứa nhỏ hơn số người nếu number_of_vehicles = 1.
- Được phép sử dụng nhiều xe.
- Nếu sử dụng nhiều xe thì number_of_vehicles phải đủ để chở toàn bộ số người.
- Tổng sức chứa = sức_chứa_mỗi_xe * number_of_vehicles phải >= số người.
- Ưu tiên phương án có tổng chi phí thấp hơn.
- Không chọn phương tiện có sức chứa quá lớn nếu có phương tiện nhỏ hơn đáp ứng được nhu cầu với chi phí thấp hơn.
- Ví dụ:
  - 2 người không nên chọn Taxi 7 chỗ nếu Taxi 4 chỗ phù hợp hơn.
  - 4 người không nên chọn Taxi 7 chỗ nếu Taxi 4 chỗ đủ chỗ.
  - 5 người có thể chọn 1 Taxi 7 chỗ hoặc nhiều xe nhỏ hơn nếu tổng chi phí thấp hơn.
- Ưu tiên ít xe hơn nếu chi phí tương đương.

QUY TẮC CHI PHÍ:
AI chỉ ước tính chi phí cơ bản, backend sẽ tính lại chính xác.

1. Chi phí di chuyển địa phương:
chi_phi_dia_phuong =
khoang_cach_giua_hai_item * gia_moi_km * number_of_vehicles

2. Chi phí quán ăn:
estimated_cost = gia_trung_binh * so_nguoi

3. Chi phí điểm tham quan:
estimated_cost = gia_trung_binh * so_nguoi

4. Chi phí chỗ ở:
estimated_cost = gia_trung_binh * so_phong

Nếu không có sức chứa phòng:
so_phong = ceil(so_nguoi / 2)

GIẢ ĐỊNH:
- estimated_cost chỉ là chi phí ước tính của item.
- estimated_day_cost là tổng estimated_cost của các item trong ngày.
- estimated_total_cost là tổng estimated_day_cost.
- estimated_transport_cost là chi phí di chuyển ước tính để đi đến item hiện tại.
- estimated_total_cost_to_item = estimated_item_cost + estimated_transport_cost.
- Với item đầu tiên trong ngày, estimated_transport_cost là chi phí đi từ điểm xuất phát hoặc chỗ ở hôm trước đến item đó.
- Với các item tiếp theo, estimated_transport_cost là chi phí đi từ item trước đó đến item hiện tại.
- Với type = "accommodation", estimated_transport_cost là chi phí đi từ địa điểm cuối cùng trong ngày đến chỗ ở.

TIME SLOT CHỈ ĐƯỢC GỒM:
- morning
- lunch
- afternoon
- dinner
- evening

QUY TẮC KIỂM TRA NGÂN SÁCH TRƯỚC KHI TRẢ KẾT QUẢ:
- Trước khi trả JSON, phải tự cộng estimated_cost của tất cả item.
- estimated_total_cost không được lớn hơn tổng ngân sách nếu có thể.
- Nếu estimated_total_cost vượt ngân sách:
  1. Giảm số địa điểm có phí cao.
  2. Chọn chỗ ở rẻ hơn.
  3. Chọn phương tiện rẻ hơn.
  4. Ưu tiên địa điểm miễn phí hoặc giá thấp.
- Nếu vẫn không thể dưới ngân sách, phải ghi rõ trong budget_note:
  "Không thể tạo lịch trình dưới ngân sách với dữ liệu hiện có".
- Không được cố tình trả estimated_total_cost vượt ngân sách mà không giải thích.

YÊU CẦU NGƯỜI DÙNG:
{cau_hoi_user}

THÔNG TIN NGÂN SÁCH:
{budget_prompt}

SỐ NGƯỜI:
{so_nguoi}

DANH SÁCH PHƯƠNG TIỆN:
{vehicles_prompt}

DANH SÁCH CHỖ Ở:
{accommodations_prompt}

DANH SÁCH ĐỊA ĐIỂM ĐI CHƠI / ĂN UỐNG:
{travel_places_prompt}

BẮT BUỘC CHỈ TRẢ JSON SẠCH.
Không markdown.
Không giải thích.
Không thêm text ngoài JSON.

JSON mẫu bắt buộc:

{{
  "days": [
    {{
      "day": 1,
      "items": [
        {{
          "id": "ma_dia_diem",
          "place_name": "Tên địa điểm",
          "type": "place",
          "start_time": "08:00",
          "end_time": "10:00",
          "time_slot": "morning",
          "is_golden_hour_used": true,
          "golden_hour_note": "Xếp trong khung giờ vàng 07:00-09:00",
          "ma_pt": "ma_phuong_tien",
          "suggested_transport_name": "Tên phương tiện",
          "estimated_item_cost": 0,
          "estimated_transport_cost": 0,
          "estimated_total_cost_to_item": 0
        }},
        {{
          "id": "ma_dia_diem_cho_o",
          "place_name": "Tên chỗ ở",
          "type": "accommodation",
          "start_time": "21:00",
          "end_time": "overnight",
          "time_slot": "evening",
          "is_golden_hour_used": false,
          "golden_hour_note": "Không áp dụng cho chỗ ở",
          "ma_pt": "ma_phuong_tien",
          "suggested_transport_name": "Tên phương tiện",
          "number_of_vehicles": 1,
          "estimated_cost": 0,
          "estimated_item_cost": 0,
          "estimated_transport_cost": 0,
          "estimated_total_cost_to_item": 0
        }}
      ],
      "estimated_day_cost": 0
    }}
  ],
  "estimated_total_cost": 0,
  "budget_note": "Nhận xét ngắn về ngân sách"
}}
"""

    @classmethod
    def len_lich_trinh_sang_tao(
        cls,
        cau_hoi_user,
        places,
        vehicles,
        so_ngay,
        so_nguoi=1,
        ngan_sach=0
    ):

        try:
            so_nguoi = int(so_nguoi or 1)
        except Exception:
            so_nguoi = 1

        vehicles = [
            v
            for v in vehicles
            if v.loai != "lien_tinh"
        ]

        accommodations, travel_places = (
            cls.split_accommodations_and_places(
                places
            )
        )

        if not accommodations:
            raise ValueError(
                "Không có chỗ ở trong danh sách địa điểm gửi vào Gemini."
            )

        if not travel_places:
            raise ValueError(
                "Không có địa điểm đi chơi/ăn uống trong danh sách gửi vào Gemini."
            )

        prompt = cls.build_prompt(
            cau_hoi_user=cau_hoi_user,
            accommodations=accommodations,
            travel_places=travel_places,
            vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi,
            ngan_sach=ngan_sach
        )

        response = cls.client.models.generate_content(
            model=cls.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        usage = getattr(
            response,
            "usage_metadata",
            None
        )

        tokens_su_dung = 0

        if usage:
            tokens_su_dung = (
                getattr(
                    usage,
                    "total_token_count",
                    0
                ) or 0
            )

        raw_response = response.text.strip()

        try:
            lich_trinh = json.loads(
                raw_response
            )
        except Exception:
            lich_trinh = cls.clean_json_response(
                raw_response
            )

        return {
            "itinerary": lich_trinh,
            "tokens_su_dung": tokens_su_dung
        }
        
    @classmethod
    def sua_lich_trinh_theo_ngan_sach(
        cls,
        lich_trinh_ai,
        cost_summary,
        cau_hoi_user,
        places,
        vehicles,
        so_ngay,
        so_nguoi,
        ngan_sach
    ):
        accommodations, travel_places = cls.split_accommodations_and_places(
            places
        )

        accommodations_prompt = cls.build_places_prompt(
            accommodations
        )

        travel_places_prompt = cls.build_places_prompt(
            travel_places
        )

        vehicles_prompt = cls.build_vehicles_prompt(
            vehicles,
            so_nguoi
        )

        prompt = f"""
Bạn là AI Travel Planner.

Lịch trình hiện tại đang vượt ngân sách.

YÊU CẦU:
- Sửa lại lịch trình để giảm chi phí.
- Giữ đúng {so_ngay} ngày.
- Mỗi ngày vẫn phải có đúng 1 item type = "accommodation".
- Chỗ ở vẫn phải là item cuối cùng trong ngày.
- Không tạo địa điểm mới.
- Không tạo phương tiện mới.
- Chỉ dùng ID địa điểm và ID phương tiện trong danh sách.
- Ưu tiên giữ các địa điểm có điểm phù hợp cao.
- Giảm hoặc bỏ các địa điểm có chi phí cao nếu cần.
- Chọn chỗ ở rẻ hơn nếu có.
- Chọn phương tiện rẻ hơn nếu hợp lý.
- Không được xếp lịch lòng vòng.
- Vẫn phải có start_time, end_time, ma_pt, number_of_vehicles.
- Vẫn phải trả JSON đúng schema items.

THÔNG TIN NGƯỜI DÙNG:
{cau_hoi_user}

NGÂN SÁCH:
{ngan_sach}

CHI PHÍ HIỆN TẠI:
{json.dumps(cost_summary, ensure_ascii=False, indent=2)}

LỊCH TRÌNH HIỆN TẠI:
{json.dumps(lich_trinh_ai, ensure_ascii=False, indent=2)}

DANH SÁCH PHƯƠNG TIỆN:
{vehicles_prompt}

DANH SÁCH CHỖ Ở:
{accommodations_prompt}

DANH SÁCH ĐỊA ĐIỂM ĐI CHƠI / ĂN UỐNG:
{travel_places_prompt}

BẮT BUỘC:
- Chỉ trả JSON sạch.
- Không markdown.
- Không giải thích.

JSON mẫu:

{{
  "days": [
    {{
      "day": 1,
      "items": [
        {{
          "id": "ma_dia_diem",
          "place_name": "Tên địa điểm",
          "type": "place",
          "start_time": "08:00",
          "end_time": "10:00",
          "time_slot": "morning",
          "is_golden_hour_used": true,
          "golden_hour_note": "Ghi chú khung giờ vàng",
          "ma_pt": "ma_phuong_tien",
          "suggested_transport_name": "Tên phương tiện",
          "number_of_vehicles": 1,
          "estimated_cost": 0,
          "estimated_transport_cost": 0,
          "estimated_total_cost_to_item": 0,
          "note": "Ghi chú ngắn"
        }},
        {{
          "id": "ma_dia_diem_cho_o",
          "place_name": "Tên chỗ ở",
          "type": "accommodation",
          "start_time": "21:00",
          "end_time": "overnight",
          "time_slot": "evening",
          "is_golden_hour_used": false,
          "golden_hour_note": "Không áp dụng cho chỗ ở",
          "ma_pt": "ma_phuong_tien",
          "suggested_transport_name": "Tên phương tiện",
          "number_of_vehicles": 1,
          "estimated_cost": 0,
          "estimated_transport_cost": 0,
          "estimated_total_cost_to_item": 0,
          "note": "Chỗ ở qua đêm"
        }}
      ],
      "estimated_day_cost": 0
    }}
  ],
  "estimated_total_cost": 0,
  "budget_note": "Nhận xét ngân sách"
}}
"""

        response = cls.client.models.generate_content(
            model=cls.MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                response_mime_type="application/json"
            )
        )

        raw_response = response.text.strip()

        try:
            return json.loads(raw_response)
        except Exception:
            return cls.clean_json_response(
                raw_response
            )    