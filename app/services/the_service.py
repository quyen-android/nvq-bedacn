from app.repositories import the_repo, loai_dia_diem_repo


class TheService:

    @staticmethod
    def get_all(db):
        return the_repo.get_all(db)

    @staticmethod
    def get_by_id(db, ma_the):
        the = the_repo.get_by_id(db, ma_the)

        if not the:
            raise ValueError("Không tìm thấy thẻ")

        return the

    @staticmethod
    def get_by_loai(db, ma_loai):
        return the_repo.get_by_loai(db, ma_loai)

    @staticmethod
    def create(db, data):
        loai = loai_dia_diem_repo.get_by_id(
            db,
            data.ma_loai
        )

        if not loai:
            raise ValueError("Không tìm thấy loại địa điểm")

        existed = the_repo.get_by_name_and_loai(
            db=db,
            ten_the=data.ten_the,
            ma_loai=data.ma_loai
        )

        if existed:
            raise ValueError("Thẻ này đã tồn tại trong loại địa điểm này")

        the = the_repo.create(db, data)

        db.commit()
        db.refresh(the)

        return the

    @staticmethod
    def update(db, ma_the, data):
        the = the_repo.get_by_id(db, ma_the)

        if not the:
            raise ValueError("Không tìm thấy thẻ")

        new_ten_the = (
            data.ten_the
            if data.ten_the is not None
            else the.ten_the
        )

        new_ma_loai = (
            data.ma_loai
            if data.ma_loai is not None
            else the.ma_loai
        )

        loai = loai_dia_diem_repo.get_by_id(
            db,
            new_ma_loai
        )

        if not loai:
            raise ValueError("Không tìm thấy loại địa điểm")

        existed = the_repo.get_by_name_and_loai(
            db=db,
            ten_the=new_ten_the,
            ma_loai=new_ma_loai
        )

        if existed and existed.ma_the != the.ma_the:
            raise ValueError("Thẻ này đã tồn tại trong loại địa điểm này")

        the = the_repo.update(
            db,
            the,
            data
        )

        db.commit()
        db.refresh(the)

        return the

    @staticmethod
    def delete(db, ma_the):
        the = the_repo.get_by_id(db, ma_the)

        if not the:
            raise ValueError("Không tìm thấy thẻ")

        the_repo.delete(db, the)

        db.commit()

        return {
            "message": "Xóa thẻ thành công"
        }