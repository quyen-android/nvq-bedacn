from app.repositories import chuyen_di_repo


class ChuyenDiService:

    @staticmethod
    def create_chuyen_di(
        db,
        data,
        current_user
    ):
        if data.ngay_ve < data.ngay_di:
            raise ValueError(
                "Ngày về phải lớn hơn hoặc bằng ngày đi"
            )

        if data.so_nguoi <= 0:
            raise ValueError(
                "Số người phải lớn hơn 0"
            )

        if data.ngan_sach < 0:
            raise ValueError(
                "Ngân sách không được âm"
            )

        chuyen_di = chuyen_di_repo.create(
            db=db,
            data=data,
            ma_nguoi_dung=current_user.ma_nguoi_dung
        )

        chuyen_di_repo.add_loai_du_lichs(
            db=db,
            ma_chuyen_di=chuyen_di.ma_chuyen_di,
            loai_du_lich_ids=data.loai_du_lich_ids
        )

        chuyen_di_repo.add_so_thichs(
            db=db,
            ma_chuyen_di=chuyen_di.ma_chuyen_di,
            so_thich_ids=data.so_thich_ids
        )

        chuyen_di_repo.add_yeu_caus(
            db=db,
            ma_chuyen_di=chuyen_di.ma_chuyen_di,
            yeu_cau_ids=data.yeu_cau_ids
        )

        db.commit()
        db.refresh(chuyen_di)

        return chuyen_di

    @staticmethod
    def get_my_chuyen_dis(
        db,
        current_user
    ):
        return chuyen_di_repo.get_all_by_user(
            db=db,
            ma_nguoi_dung=current_user.ma_nguoi_dung
        )

    @staticmethod
    def get_chuyen_di_detail(
        db,
        ma_chuyen_di,
        current_user
    ):
        chuyen_di = chuyen_di_repo.get_by_id_and_user(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            ma_nguoi_dung=current_user.ma_nguoi_dung
        )

        if not chuyen_di:
            raise ValueError(
                "Không tìm thấy chuyến đi"
            )

        return chuyen_di

    @staticmethod
    def update_chuyen_di(
        db,
        ma_chuyen_di,
        data,
        current_user
    ):
        chuyen_di = chuyen_di_repo.get_by_id_and_user(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            ma_nguoi_dung=current_user.ma_nguoi_dung
        )

        if not chuyen_di:
            raise ValueError(
                "Không tìm thấy chuyến đi"
            )

        if data.ngay_ve is not None:
            if data.ngay_ve < chuyen_di.ngay_di:
                raise ValueError(
                    "Ngày về phải lớn hơn hoặc bằng ngày đi"
                )

        if data.ngan_sach is not None:
            if data.ngan_sach < 0:
                raise ValueError(
                    "Ngân sách không được âm"
                )

        chuyen_di = chuyen_di_repo.update(
            db=db,
            chuyen_di=chuyen_di,
            data=data
        )

        db.commit()
        db.refresh(chuyen_di)

        return chuyen_di

    @staticmethod
    def delete_chuyen_di(
        db,
        ma_chuyen_di,
        current_user
    ):
        chuyen_di = chuyen_di_repo.get_by_id_and_user(
            db=db,
            ma_chuyen_di=ma_chuyen_di,
            ma_nguoi_dung=current_user.ma_nguoi_dung
        )

        if not chuyen_di:
            raise ValueError(
                "Không tìm thấy chuyến đi"
            )

        chuyen_di_repo.delete(
            db=db,
            chuyen_di=chuyen_di
        )

        db.commit()

        return {
            "message": "Xóa chuyến đi thành công"
        }