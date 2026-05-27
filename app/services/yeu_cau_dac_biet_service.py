from app.repositories import yeu_cau_dac_biet_repo


class YeuCauDacBietService:

    @staticmethod
    def get_all(db):
        return yeu_cau_dac_biet_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_yeu_cau):
        item = yeu_cau_dac_biet_repo.get_by_id(
            db,
            ma_yeu_cau
        )

        if not item:
            raise ValueError("Không tìm thấy yêu cầu đặc biệt")

        return item

    @staticmethod
    def create(db, data):
        existed = yeu_cau_dac_biet_repo.get_by_name(
            db,
            data.ten_yeu_cau
        )

        if existed:
            raise ValueError("Yêu cầu đặc biệt đã tồn tại")

        item = yeu_cau_dac_biet_repo.create(
            db,
            data
        )

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def update(db, ma_yeu_cau, data):
        item = yeu_cau_dac_biet_repo.get_by_id(
            db,
            ma_yeu_cau
        )

        if not item:
            raise ValueError("Không tìm thấy yêu cầu đặc biệt")

        if data.ten_yeu_cau:
            existed = yeu_cau_dac_biet_repo.get_by_name(
                db,
                data.ten_yeu_cau
            )

            if existed and existed.ma_yeu_cau != item.ma_yeu_cau:
                raise ValueError("Yêu cầu đặc biệt đã tồn tại")

        item = yeu_cau_dac_biet_repo.update(
            db,
            item,
            data
        )

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def delete(db, ma_yeu_cau):
        item = yeu_cau_dac_biet_repo.get_by_id(
            db,
            ma_yeu_cau
        )

        if not item:
            raise ValueError("Không tìm thấy yêu cầu đặc biệt")

        yeu_cau_dac_biet_repo.delete(
            db,
            item
        )

        db.commit()

        return {
            "message": "Xóa yêu cầu đặc biệt thành công"
        }