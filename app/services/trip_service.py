from app.repositories import chuyen_di_repo


class TripService:

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