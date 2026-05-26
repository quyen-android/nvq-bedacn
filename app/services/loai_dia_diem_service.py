from app.repositories import loai_dia_diem_repo


class LoaiDiaDiemService:

    @staticmethod
    def get_all(db):
        return loai_dia_diem_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_loai):
        loai = loai_dia_diem_repo.get_by_id(
            db,
            ma_loai
        )

        if not loai:
            raise ValueError(
                "Không tìm thấy loại địa điểm"
            )

        return loai

    @staticmethod
    def create(db, data):
        existed = (
            loai_dia_diem_repo.get_by_name(
                db,
                data.ten_loai
            )
        )

        if existed:
            raise ValueError(
                "Loại địa điểm đã tồn tại"
            )

        loai = (
            loai_dia_diem_repo.create(
                db,
                data
            )
        )

        db.commit()
        db.refresh(loai)

        return loai

    @staticmethod
    def update(
        db,
        ma_loai,
        data
    ):
        loai = (
            loai_dia_diem_repo.get_by_id(
                db,
                ma_loai
            )
        )

        if not loai:
            raise ValueError(
                "Không tìm thấy loại địa điểm"
            )

        if data.ten_loai:
            existed = (
                loai_dia_diem_repo.get_by_name(
                    db,
                    data.ten_loai
                )
            )

            if (
                existed and
                existed.ma_loai != loai.ma_loai
            ):
                raise ValueError(
                    "Loại địa điểm đã tồn tại"
                )

        loai = (
            loai_dia_diem_repo.update(
                db,
                loai,
                data
            )
        )

        db.commit()
        db.refresh(loai)

        return loai

    @staticmethod
    def delete(
        db,
        ma_loai
    ):
        loai = (
            loai_dia_diem_repo.get_by_id(
                db,
                ma_loai
            )
        )

        if not loai:
            raise ValueError(
                "Không tìm thấy loại địa điểm"
            )

        loai_dia_diem_repo.delete(
            db,
            loai
        )

        db.commit()

        return {
            "message":
            "Xóa loại địa điểm thành công"
        }