from app.repositories import tinh_repo


class TinhService:

    @staticmethod
    def get_all(db):
        return tinh_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_tinh):
        tinh = tinh_repo.get_by_id(db, ma_tinh)

        if not tinh:
            raise ValueError("Không tìm thấy tỉnh")

        return tinh

    @staticmethod
    def create(db, data):
        existed = tinh_repo.get_by_name_and_country(
            db=db,
            ten_tinh=data.ten_tinh,
            quoc_gia=data.quoc_gia
        )

        if existed:
            raise ValueError("Tỉnh này đã tồn tại")

        tinh = tinh_repo.create(db, data)

        db.commit()
        db.refresh(tinh)

        return tinh

    @staticmethod
    def update(db, ma_tinh, data):
        tinh = tinh_repo.get_by_id(db, ma_tinh)

        if not tinh:
            raise ValueError("Không tìm thấy tỉnh")

        new_ten_tinh = (
            data.ten_tinh
            if data.ten_tinh is not None
            else tinh.ten_tinh
        )

        new_quoc_gia = (
            data.quoc_gia
            if data.quoc_gia is not None
            else tinh.quoc_gia
        )

        existed = tinh_repo.get_by_name_and_country(
            db=db,
            ten_tinh=new_ten_tinh,
            quoc_gia=new_quoc_gia
        )

        if existed and existed.ma_tinh != tinh.ma_tinh:
            raise ValueError("Tỉnh này đã tồn tại")

        tinh = tinh_repo.update(db, tinh, data)

        db.commit()
        db.refresh(tinh)

        return tinh

    @staticmethod
    def delete(db, ma_tinh):
        tinh = tinh_repo.get_by_id(db, ma_tinh)

        if not tinh:
            raise ValueError("Không tìm thấy tỉnh")

        tinh_repo.delete(db, tinh)

        db.commit()

        return {
            "message": "Xóa tỉnh thành công"
        }