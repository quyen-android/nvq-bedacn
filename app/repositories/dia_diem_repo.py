from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models import DiaDiem, LoaiDiaDiem, The, TheDiaDiem


def filter_dia_diem(
    db: Session,
    loai=None,
    search=None,
    tags=None,
    min_gia=None,
    max_gia=None,
    danh_gia=None
):
    query = db.query(DiaDiem)

    query = query.join(LoaiDiaDiem, DiaDiem.ma_loai == LoaiDiaDiem.ma_loai)

    # lọc theo loại 
    if loai:
        query = query.filter(LoaiDiaDiem.ten_loai == loai)

    # search sâu
    if search:
        keywords = search.split()

        for kw in keywords:
            query = query.filter(
                or_(
                    DiaDiem.ten.ilike(f"%{kw}%"),
                    DiaDiem.mo_ta.ilike(f"%{kw}%")
                )
            )

    # filter tag
    if tags:
        query = query.join(TheDiaDiem).join(The).filter(
            The.ten_the.in_(tags)
        )

    # giá
    if min_gia and max_gia:
        query = query.filter(DiaDiem.gia_trung_binh.between(min_gia, max_gia))

    # rating
    if danh_gia:
        query = query.filter(DiaDiem.danh_gia >= danh_gia)

    return query.distinct().all()