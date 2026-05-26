from app.repositories import so_thich_am_thuc_repo


class SoThichAmThucService:

    @staticmethod
    def get_all(db):
        return so_thich_am_thuc_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_so_thich):
        item = so_thich_am_thuc_repo.get_by_id(db, ma_so_thich)

        if not item:
            raise ValueError("Không tìm thấy sở thích ẩm thực")

        return item

    @staticmethod
    def create(db, data):
        existed = so_thich_am_thuc_repo.get_by_name(
            db,
            data.ten_so_thich
        )

        if existed:
            raise ValueError("Sở thích ẩm thực đã tồn tại")

        item = so_thich_am_thuc_repo.create(db, data)

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def update(db, ma_so_thich, data):
        item = so_thich_am_thuc_repo.get_by_id(
            db,
            ma_so_thich
        )

        if not item:
            raise ValueError("Không tìm thấy sở thích ẩm thực")

        if data.ten_so_thich:
            existed = so_thich_am_thuc_repo.get_by_name(
                db,
                data.ten_so_thich
            )

            if existed and existed.ma_so_thich != item.ma_so_thich:
                raise ValueError("Sở thích ẩm thực đã tồn tại")

        item = so_thich_am_thuc_repo.update(
            db,
            item,
            data
        )

        db.commit()
        db.refresh(item)

        return item

    @staticmethod
    def delete(db, ma_so_thich):
        item = so_thich_am_thuc_repo.get_by_id(
            db,
            ma_so_thich
        )

        if not item:
            raise ValueError("Không tìm thấy sở thích ẩm thực")

        so_thich_am_thuc_repo.delete(db, item)

        db.commit()

        return {
            "message": "Xóa sở thích ẩm thực thành công"
        }