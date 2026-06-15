from app.services.gemini_service import GeminiService
from app.services.kiem_tra_lich_trinh_service import KiemTraLichTrinhService
from app.services.sua_lich_trinh_service import SuaLichTrinhService
from app.services.toi_uu_tuyen_duong_service import ToiUuTuyenDuongService
from app.services.kiem_tra_gio_mo_cua_service import KiemTraGioMoCuaService
from app.services.du_toan_chi_phi_service import DuToanChiPhiService


class LapLichAIService:
    MAX_REPAIR_BUDGET = 3

    @classmethod
    def lap_lich(
        cls,
        cau_hoi_user,
        places,
        vehicles,
        so_ngay,
        so_nguoi,
        ngan_sach
    ):
        lich_trinh_ai = GeminiService.len_lich_trinh_sang_tao(
            cau_hoi_user=cau_hoi_user,
            places=places,
            vehicles=vehicles,
            so_ngay=so_ngay,
            so_nguoi=so_nguoi,
            ngan_sach=ngan_sach
        )

        for lan_sua in range(cls.MAX_REPAIR_BUDGET + 1):
            loi = KiemTraLichTrinhService.kiem_tra(
                lich_trinh_ai=lich_trinh_ai,
                db_places=places,
                db_vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi
            )

            if loi:
                lich_trinh_ai = SuaLichTrinhService.sua(
                    lich_trinh_ai=lich_trinh_ai,
                    db_places=places,
                    db_vehicles=vehicles,
                    so_ngay=so_ngay,
                    so_nguoi=so_nguoi
                )

            lich_trinh_ai = ToiUuTuyenDuongService.toi_uu(
                lich_trinh_ai=lich_trinh_ai,
                db_places=places
            )

            loi_gio = KiemTraGioMoCuaService.kiem_tra(
                lich_trinh_ai=lich_trinh_ai,
                db_places=places
            )

            lich_trinh_ai = DuToanChiPhiService.tinh_du_toan(
                lich_trinh_ai=lich_trinh_ai,
                db_places=places,
                db_vehicles=vehicles,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach
            )

            cost_summary = lich_trinh_ai.get(
                "cost_summary",
                {}
            )

            if not cost_summary.get("vuot_ngan_sach"):
                lich_trinh_ai["validation"] = {
                    "hop_le": True,
                    "loi": loi,
                    "loi_gio_mo_cua": loi_gio,
                    "so_lan_sua_ngan_sach": lan_sua
                }

                return lich_trinh_ai

            if lan_sua >= cls.MAX_REPAIR_BUDGET:
                lich_trinh_ai["validation"] = {
                    "hop_le": False,
                    "loi": loi,
                    "loi_gio_mo_cua": loi_gio,
                    "ly_do": "Không thể sửa lịch trình dưới ngân sách sau nhiều lần thử",
                    "so_lan_sua_ngan_sach": lan_sua
                }

                return lich_trinh_ai

            lich_trinh_ai = GeminiService.sua_lich_trinh_theo_ngan_sach(
                lich_trinh_ai=lich_trinh_ai,
                cost_summary=cost_summary,
                cau_hoi_user=cau_hoi_user,
                places=places,
                vehicles=vehicles,
                so_ngay=so_ngay,
                so_nguoi=so_nguoi,
                ngan_sach=ngan_sach
            )

        return lich_trinh_ai