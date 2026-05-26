from app.repositories import loai_du_lich_repo


class LoaiDuLichService:

    @staticmethod
    def get_all(db):
        return loai_du_lich_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_loai_du_lich):
        item = loai_du_lich_repo.get_by_id(
            db,
            ma_loai_du_lich
        )

        if not item:
            raise ValueError("Không tìm thấy loại du lịch")

        return item

    @staticmethod
    def create(db, data):
        existed = loai_du_lich_repo.get_by_name(
            db,
            data.ten_loai
        )

        if existed:
            raise ValueError("Loại du lịch đã tồn tại")

        item = loai_du_lich_repo.create(
            db,
            data
        )

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def update(db, ma_loai_du_lich, data):
        item = loai_du_lich_repo.get_by_id(
            db,
            ma_loai_du_lich
        )

        if not item:
            raise ValueError("Không tìm thấy loại du lịch")

        if data.ten_loai:
            existed = loai_du_lich_repo.get_by_name(
                db,
                data.ten_loai
            )

            if existed and existed.ma_loai_du_lich != item.ma_loai_du_lich:
                raise ValueError("Loại du lịch đã tồn tại")

        item = loai_du_lich_repo.update(
            db,
            item,
            data
        )

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def delete(db, ma_loai_du_lich):
        item = loai_du_lich_repo.get_by_id(
            db,
            ma_loai_du_lich
        )

        if not item:
            raise ValueError("Không tìm thấy loại du lịch")

        loai_du_lich_repo.delete(
            db,
            item
        )

        db.commit()

        return {
            "message": "Xóa loại du lịch thành công"
        }