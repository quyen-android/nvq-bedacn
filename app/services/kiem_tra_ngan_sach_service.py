class KiemTraNganSachService:

    @staticmethod
    def kiem_tra(
        tong_chi_phi_result
    ):
        ngan_sach = float(
            tong_chi_phi_result.get("ngan_sach") or 0
        )

        tong_sau_phu_phi = float(
            tong_chi_phi_result.get("tong_sau_phu_phi") or 0
        )

        if ngan_sach <= 0:
            return {
                "hop_le": True,
                "vuot_ngan_sach": False,
                "ngan_sach": ngan_sach,
                "tong_chi_phi": tong_sau_phu_phi,
                "so_tien_vuot": 0,
                "so_tien_con_lai": 0,
                "thong_bao": "Chuyến đi không đặt giới hạn ngân sách"
            }

        vuot = tong_sau_phu_phi > ngan_sach

        return {
            "hop_le": not vuot,
            "vuot_ngan_sach": vuot,
            "ngan_sach": round(ngan_sach, 0),
            "tong_chi_phi": round(tong_sau_phu_phi, 0),
            "so_tien_vuot": round(
                max(tong_sau_phu_phi - ngan_sach, 0),
                0
            ),
            "so_tien_con_lai": round(
                max(ngan_sach - tong_sau_phu_phi, 0),
                0
            ),
            "thong_bao": (
                "Chi phí vượt ngân sách"
                if vuot
                else "Chi phí nằm trong ngân sách"
            )
        }