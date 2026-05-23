from app.models.chuyen_di import ChuyenDi
from app.models.loai_du_lich_cd import LoaiDuLichCD
from app.models.loai_du_lich import LoaiDuLich
from app.models.so_thich_cd import SoThichCD
from app.models.so_thich_am_thuc import SoThichAmThuc
from app.models.yeu_cau_cd import YeuCauCD
from app.models.yeu_cau_dac_biet import YeuCauDacBiet

def create(
    db,
    data,
    ma_nguoi_dung
):
    chuyen_di = ChuyenDi(
        ma_nguoi_dung=ma_nguoi_dung,
        ma_pt=data.ma_pt,
        ma_tinh_di=data.ma_tinh_di,
        ma_tinh_den=data.ma_tinh_den,
        ten_chuyen_di=data.ten_chuyen_di,
        ngay_di=data.ngay_di,
        ngay_ve=data.ngay_ve,
        so_nguoi=data.so_nguoi,
        ngan_sach=data.ngan_sach,
        trang_thai="ban_nhap"
    )

    db.add(chuyen_di)
    db.flush()

    return chuyen_di

def add_loai_du_lichs(
    db,
    ma_chuyen_di,
    loai_du_lich_ids
):
    for ma_loai_du_lich in loai_du_lich_ids:
        item = LoaiDuLichCD(
            ma_chuyen_di=ma_chuyen_di,
            ma_loai_du_lich=ma_loai_du_lich
        )

        db.add(item)


def add_so_thichs(
    db,
    ma_chuyen_di,
    so_thich_ids
):
    for ma_so_thich in so_thich_ids:
        item = SoThichCD(
            ma_chuyen_di=ma_chuyen_di,
            ma_so_thich=ma_so_thich
        )

        db.add(item)

def add_yeu_caus(
    db,
    ma_chuyen_di,
    yeu_cau_ids
):
    for ma_yeu_cau in yeu_cau_ids:
        item = YeuCauCD(
            ma_chuyen_di=ma_chuyen_di,
            ma_yeu_cau=ma_yeu_cau
        )

        db.add(item)
        
def get_by_id(db, ma_chuyen_di):
    return (
        db.query(ChuyenDi)
        .filter(
            ChuyenDi.ma_chuyen_di == ma_chuyen_di
        )
        .first()
    )


def get_loai_du_lich_by_chuyen_di(db, ma_chuyen_di):
    return (
        db.query(LoaiDuLich.ten_loai)
        .join(
            LoaiDuLichCD,
            LoaiDuLich.ma_loai_du_lich
            == LoaiDuLichCD.ma_loai_du_lich
        )
        .filter(
            LoaiDuLichCD.ma_chuyen_di == ma_chuyen_di
        )
        .all()
    )


def get_so_thich_am_thuc_by_chuyen_di(db, ma_chuyen_di):
    return (
        db.query(SoThichAmThuc.ten_so_thich)
        .join(
            SoThichCD,
            SoThichAmThuc.ma_so_thich
            == SoThichCD.ma_so_thich
        )
        .filter(
            SoThichCD.ma_chuyen_di == ma_chuyen_di
        )
        .all()
    )

def get_yeu_cau_dac_biet_by_chuyen_di(db, ma_chuyen_di):
    return (
        db.query(YeuCauDacBiet.ten_yeu_cau)
        .join(
            YeuCauCD,
            YeuCauDacBiet.ma_yeu_cau
            == YeuCauCD.ma_yeu_cau
        )
        .filter(
            YeuCauCD.ma_chuyen_di == ma_chuyen_di
        )
        .all()
    )