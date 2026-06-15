from app.repositories import phuong_tien_repo


class PhuongTienAIService:

    @staticmethod
    def format_transport_for_prompt(phuong_tiens):
        if not phuong_tiens:
            return "Không có dữ liệu phương tiện địa phương."

        lines = []

        for pt in phuong_tiens:
            lines.append(
                f"- ID: {pt.ma_pt} | "
                f"Tên: {pt.ten_pt} | "
                f"Loại: {pt.loai} | "
                f"Tốc độ TB: {pt.toc_do_tb} km/h | "
                f"Giá mỗi km: {pt.gia_moi_km} VNĐ | "
                f"Sức chứa: {pt.suc_chua} người"
            )

        return "\n".join(lines)

    @classmethod
    def get_local_transport_prompt(cls, db):
        phuong_tiens = phuong_tien_repo.get_all_local_vehicles(db)

        return cls.format_transport_for_prompt(
            phuong_tiens
        )