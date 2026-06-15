from app.models.nhat_ky_ai import NhatKyAI


class NhatKyAIService:

    @staticmethod
    def tao_log(
        db,
        ma_nguoi_dung=None,
        ma_chuyen_di=None,
        cau_hoi=None,
        cau_tra_loi=None,
        ngu_canh=None,
        model=None,
        tokens_su_dung=None,
        tg_phan_hoi=None
    ):
        log = NhatKyAI(
            ma_nguoi_dung=ma_nguoi_dung,
            ma_chuyen_di=ma_chuyen_di,
            cau_hoi=cau_hoi,
            cau_tra_loi=cau_tra_loi,
            ngu_canh=ngu_canh,
            model=model,
            tokens_su_dung=tokens_su_dung,
            tg_phan_hoi=tg_phan_hoi
        )

        db.add(log)
        db.flush()

        return log

    @staticmethod
    def get_my_logs(db, current_user):
        return (
            db.query(NhatKyAI)
            .filter(
                NhatKyAI.ma_nguoi_dung
                == current_user.ma_nguoi_dung
            )
            .order_by(NhatKyAI.ngay_tao.desc())
            .all()
        )

    @staticmethod
    def danh_gia_log(
        db,
        ma_log,
        danh_gia,
        current_user
    ):
        if danh_gia < 1 or danh_gia > 5:
            raise ValueError("Đánh giá phải từ 1 đến 5")

        log = (
            db.query(NhatKyAI)
            .filter(
                NhatKyAI.ma_log == ma_log,
                NhatKyAI.ma_nguoi_dung
                == current_user.ma_nguoi_dung
            )
            .first()
        )

        if not log:
            raise ValueError("Không tìm thấy nhật ký AI")

        log.danh_gia = danh_gia

        db.commit()
        db.refresh(log)

        return log