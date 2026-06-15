import json
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

from app.models.phuong_tien import PhuongTien
from app.models.chuyen_di import ChuyenDi
from app.models.dia_diem import DiaDiem

from app.services.gemini_service import GeminiService
from app.services.rag_service import RagService
from app.services.xep_hang_service import XepHangService

from app.services.kiem_tra_lich_trinh_service import KiemTraLichTrinhService
from app.services.sua_lich_trinh_service import SuaLichTrinhService
from app.services.toi_uu_tuyen_duong_service import ToiUuTuyenDuongService
from app.services.kiem_tra_gio_mo_cua_service import KiemTraGioMoCuaService
from app.services.du_toan_chi_phi_service import DuToanChiPhiService
from app.services.luu_lich_trinh_ai_service import (LuuLichTrinhAIService)

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def save_json(filename, data):
    with open(
        filename,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=2,
            default=str
        )

    print(f"💾 Đã lưu {filename}")


def get_trip_info(db):
    chuyen_di = (
        db.query(ChuyenDi)
        .order_by(desc(ChuyenDi.ngay_tao))
        .first()
    )

    if not chuyen_di:
        raise ValueError(
            "Không tìm thấy chuyến đi nào trong Database"
        )

    tinh_den = (
        chuyen_di.tinh_den.ten_tinh
        if chuyen_di.tinh_den
        else "Đà Nẵng"
    )

    if chuyen_di.ngay_di and chuyen_di.ngay_ve:
        so_ngay = (
            chuyen_di.ngay_ve
            - chuyen_di.ngay_di
        ).days + 1
    else:
        so_ngay = 3

    so_nguoi = chuyen_di.so_nguoi or 1

    ngan_sach = (
        float(chuyen_di.ngan_sach)
        if chuyen_di.ngan_sach
        else 4000000.0
    )

    ds_yeu_cau = []

    if hasattr(chuyen_di, "yeu_caus") and chuyen_di.yeu_caus:
        for yc in chuyen_di.yeu_caus:
            if hasattr(yc, "noi_dung"):
                ds_yeu_cau.append(yc.noi_dung)
            elif hasattr(yc, "ten_yeu_cau"):
                ds_yeu_cau.append(yc.ten_yeu_cau)

    if ds_yeu_cau:
        cau_hoi_user = f"Yêu cầu: {', '.join(ds_yeu_cau)}."
    else:
        cau_hoi_user = (
            f"Lên lịch trình du lịch khám phá tự động tại {tinh_den}."
        )

    if chuyen_di.ten_chuyen_di:
        cau_hoi_user += (
            f" Tên chuyến đi: {chuyen_di.ten_chuyen_di}."
        )

    return {
        "chuyen_di": chuyen_di,
        "tinh_den": tinh_den,
        "so_ngay": so_ngay,
        "so_nguoi": so_nguoi,
        "ngan_sach": ngan_sach,
        "cau_hoi_user": cau_hoi_user
    }


def get_local_vehicles(db):
    return (
        db.query(PhuongTien)
        .filter(PhuongTien.loai != "lien_tinh")
        .all()
    )


def search_and_rank_places(cau_hoi_user, tinh_den, so_ngay):
    rag_results = RagService.search_places(
        query=cau_hoi_user,
        tinh=tinh_den,
        so_ngay=so_ngay
    )

    if not rag_results:
        raise ValueError(
            f"RAG không tìm thấy địa điểm tại tỉnh {tinh_den}"
        )

    ranked_places = XepHangService.rank_places(
        rag_results
    )

    return ranked_places


def get_rag_place_id(place):
    return (
        place.get("ma_dia_diem")
        or place.get("metadata", {}).get("ma_dia_diem")
    )


def get_db_places_from_rag(db, rag_places):
    ids = []

    for place in rag_places:
        ma_dia_diem = get_rag_place_id(place)

        if ma_dia_diem:
            ids.append(str(ma_dia_diem))

    ids = list(set(ids))

    if not ids:
        return []

    db_places = (
        db.query(DiaDiem)
        .filter(DiaDiem.ma_dia_diem.in_(ids))
        .all()
    )

    return db_places


def print_places(rag_places):
    print("\n=== DANH SÁCH ĐỊA ĐIỂM GỬI GEMINI ===")

    for idx, place in enumerate(rag_places, start=1):
        metadata = place.get("metadata", {})
        ranking = place.get("ranking", {})

        print(
            f"{idx}. "
            f"{metadata.get('ten')} | "
            f"{metadata.get('loai')} | "
            f"score={ranking.get('final_score', 0)}"
        )


def print_db_places(db_places):
    print("\n=== DANH SÁCH ĐỊA ĐIỂM DB DÙNG ĐỂ VALIDATE/COST ===")

    for idx, place in enumerate(db_places, start=1):
        ten_loai = (
            place.loai.ten_loai
            if place.loai
            else ""
        )

        print(
            f"{idx}. {place.ten} | {ten_loai} | {place.ma_dia_diem}"
        )


def process_itinerary_once(
    lich_trinh_json,
    rag_places,
    db_places,
    vehicles,
    so_ngay,
    so_nguoi,
    ngan_sach
):
    print("\n🔎 Kiểm tra lịch trình...")

    loi_co_ban = KiemTraLichTrinhService.kiem_tra(
        lich_trinh_ai=lich_trinh_json,
        db_places=db_places,
        db_vehicles=vehicles,
        so_ngay=so_ngay,
        so_nguoi=so_nguoi
    )

    if loi_co_ban:
        print("⚠️ Có lỗi cơ bản, đang sửa:")

        for loi in loi_co_ban:
            print("-", loi)

        lich_trinh_json = SuaLichTrinhService.sua(
            lich_trinh_ai=lich_trinh_json,
            db_places=db_places,
            db_vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi
        )
    else:
        print("✅ Lịch trình cơ bản hợp lệ")

    print("\n🧭 Tối ưu tuyến đường...")

    lich_trinh_json = ToiUuTuyenDuongService.toi_uu(
        lich_trinh_ai=lich_trinh_json,
        db_places=db_places
    )

    print("\n🕒 Kiểm tra giờ mở cửa...")

    loi_gio = KiemTraGioMoCuaService.kiem_tra(
        lich_trinh_ai=lich_trinh_json,
        db_places=db_places
    )

    if loi_gio:
        print("⚠️ Có lỗi giờ mở cửa:")

        for loi in loi_gio:
            print("-", loi)
    else:
        print("✅ Không có lỗi giờ mở cửa")

    print("\n💰 Tính dự toán chi phí trên JSON...")

    lich_trinh_json = DuToanChiPhiService.tinh_du_toan(
        lich_trinh_ai=lich_trinh_json,
        db_places=db_places,
        db_vehicles=vehicles,
        so_nguoi=so_nguoi,
        ngan_sach=ngan_sach
    )

    cost_summary = lich_trinh_json.get(
        "cost_summary",
        {}
    )

    print("Tổng sau phụ phí:", cost_summary.get("tong_sau_phu_phi"))
    print("Ngân sách:", cost_summary.get("ngan_sach"))
    print("Vượt ngân sách:", cost_summary.get("vuot_ngan_sach"))
    print("Số tiền vượt:", cost_summary.get("so_tien_vuot"))
    print("Số tiền còn lại:", cost_summary.get("so_tien_con_lai"))

    lich_trinh_json["validation"] = {
        "loi_co_ban": loi_co_ban,
        "loi_gio_mo_cua": loi_gio,
        "vuot_ngan_sach": cost_summary.get(
            "vuot_ngan_sach",
            False
        )
    }

    return lich_trinh_json


def test_full_gemini_planner():
    db = SessionLocal()

    try:
        print("=== BẮT ĐẦU KIỂM THỬ FULL GEMINI PLANNER ===")

        print("\n📥 1. Lấy chuyến đi gần nhất...")

        trip_info = get_trip_info(db)

        chuyen_di = trip_info["chuyen_di"]
        tinh_den = trip_info["tinh_den"]
        so_ngay = trip_info["so_ngay"]
        so_nguoi = trip_info["so_nguoi"]
        ngan_sach = trip_info["ngan_sach"]
        cau_hoi_user = trip_info["cau_hoi_user"]

        print("Mã chuyến đi:", chuyen_di.ma_chuyen_di)
        print("Tỉnh đến:", tinh_den)
        print("Ngày đi:", chuyen_di.ngay_di)
        print("Ngày về:", chuyen_di.ngay_ve)
        print("Số ngày:", so_ngay)
        print("Số người:", so_nguoi)
        print("Ngân sách:", ngan_sach)
        print("Prompt:", cau_hoi_user)

        print("\n📥 2. Lấy phương tiện local...")

        vehicles = get_local_vehicles(db)

        if not vehicles:
            print("❌ Không có phương tiện local")
            return

        print("Số phương tiện:", len(vehicles))

        for vehicle in vehicles:
            print(
                "-",
                vehicle.ten_pt,
                "|",
                vehicle.loai,
                "| sức chứa:",
                vehicle.suc_chua,
                "| giá/km:",
                vehicle.gia_moi_km
            )

        print(f"\n🔍 3. RAG + Ranking tại '{tinh_den}'...")

        rag_places = search_and_rank_places(
            cau_hoi_user=cau_hoi_user,
            tinh_den=tinh_den,
            so_ngay=so_ngay
        )

        all_places = rag_places

        db_places = get_db_places_from_rag(
            db,
            all_places
        )

        if not db_places:
            print("❌ Không lấy được địa điểm DB từ RAG")
            return

        print("Số địa điểm RAG gửi Gemini:", len(all_places))
        print("Số địa điểm DB dùng validate/cost:", len(db_places))

        print_places(all_places)
        print_db_places(db_places)

        save_json(
            "all_places.json",
            all_places
        )

        print("\n🤖 4. Gemini sinh lịch trình lần đầu...")
        print("Model:", settings.GEMINI_MODEL)

        lich_trinh_json = GeminiService.len_lich_trinh_sang_tao(
            cau_hoi_user=cau_hoi_user,
            places=all_places,
            vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi,
            ngan_sach=ngan_sach
        )

        save_json(
            "itinerary_raw.json",
            lich_trinh_json
        )

        MAX_REPAIR_BUDGET = 3

        for lan_sua in range(MAX_REPAIR_BUDGET + 1):
            print("\n" + "=" * 80)
            print(f"VÒNG KIỂM TRA / SỬA NGÂN SÁCH: {lan_sua}")
            print("=" * 80)

            lich_trinh_json = process_itinerary_once(
                lich_trinh_json=lich_trinh_json,
                rag_places=all_places,
                db_places=db_places,
                vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach
            )

            save_json(
                f"itinerary_checked_round_{lan_sua}.json",
                lich_trinh_json
            )

            cost_summary = lich_trinh_json.get(
                "cost_summary",
                {}
            )

            if not cost_summary.get("vuot_ngan_sach"):
                print("\n✅ Lịch trình đã nằm trong ngân sách")
                break

            if lan_sua >= MAX_REPAIR_BUDGET:
                print(
                    "\n❌ Không thể sửa dưới ngân sách sau nhiều lần thử"
                )
                break

            print("\n⚠️ Lịch trình vượt ngân sách, gửi Gemini sửa lại...")

            lich_trinh_json = GeminiService.sua_lich_trinh_theo_ngan_sach(
                lich_trinh_ai=lich_trinh_json,
                cost_summary=cost_summary,
                cau_hoi_user=cau_hoi_user,
                places=all_places,
                vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach
            )

            save_json(
                f"itinerary_repaired_by_gemini_round_{lan_sua}.json",
                lich_trinh_json
            )

        print("\n🎉 KẾT QUẢ CUỐI CÙNG:")
        print("-" * 80)

        print(
            json.dumps(
                lich_trinh_json,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        )

        print("-" * 80)

        save_json(
            "itinerary_final.json",
            lich_trinh_json
        )


        print("\n💾 Đang lưu lịch trình vào DB...")

        result = LuuLichTrinhAIService.luu(
            db=db,
            chuyen_di=chuyen_di,
            lich_trinh_ai=lich_trinh_json
        )

        print(result)
        if (
            isinstance(lich_trinh_json, dict)
            and "days" in lich_trinh_json
        ):
            print(
                "✅ Test hoàn tất với mã chuyến đi:",
                chuyen_di.ma_chuyen_di
            )
            print("⚠️ Đây mới là JSON sau kiểm tra, chưa lưu DB.")
        else:
            print("❌ JSON thiếu trường days.")

    except Exception as e:
        print("\n❌ Lỗi khi chạy full test:", str(e))

    finally:
        db.close()
        print("\n🔒 Đã đóng kết nối Database.")

    
if __name__ == "__main__":
    test_full_gemini_planner()