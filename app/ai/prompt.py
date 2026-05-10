class PromptBuilder:

    @staticmethod
    def build_itinerary_prompt(request, places_context):

        return f"""
Bạn là AI tạo lịch trình du lịch.

QUY TẮC BẮT BUỘC:

1. CHỈ được dùng địa điểm có trong danh sách.
2. KHÔNG được tự tạo tên địa điểm.
3. Nếu không đủ dữ liệu → trả:
{{
  "tong_chi_phi": 0,
  "lich_trinh": []
}}

4. Chỉ trả JSON hợp lệ.
5. Không markdown.
6. Không giải thích.
7. Không thêm text ngoài JSON.
8. Tổng chi phí không vượt quá ngân sách.
9. Mỗi địa điểm phải giống chính xác tên trong dữ liệu.
10. Nếu địa điểm không tồn tại trong dữ liệu thì không được sử dụng.
11. Mỗi địa điểm BẮT BUỘC phải có:
- gio_bat_dau
- gio_ket_thuc

THÔNG TIN:

- Ngày đi: {request.ngay_di}
- Ngày về: {request.ngay_ve}
- Ngân sách: {request.ngan_sach}
- Số người: {request.so_nguoi}

LOẠI DU LỊCH:
{', '.join(request.loai_du_lich)}

YÊU CẦU:
{', '.join(request.yeu_cau_dac_biet)}

ẨM THỰC:
{', '.join(request.so_thich_am_thuc)}

DANH SÁCH ĐỊA ĐIỂM:
{places_context}

JSON MẪU:

{{
  "tong_chi_phi": 0,
  "lich_trinh": [
    {{
      "ngay": "2026-05-08",
      "tieu_de": "Ngày 1",
      "chi_phi_ngay": 0,
      "dia_diem": [
        {{
          "ten": "",
          "gio_bat_dau": "08:00",
          "gio_ket_thuc": "10:00",
          "chi_phi": 0
        }}
      ]
    }}
  ]
}}

CHỈ TRẢ JSON.
"""