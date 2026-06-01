from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_

from app.models import (
    DiaDiem,
    LoaiDiaDiem,
    The,
    TheDiaDiem,
)


def filter_public_places(
    db,
    ma_loai=None,
    ma_tinh=None,
    min_price=None,
    max_price=None,
    min_rating=None,
    tag_ids=None,
    keyword=None
):
    query = (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.khung_gio_vangs),
            joinedload(DiaDiem.thes)
        )
    )

    if ma_loai:
        query = query.filter(DiaDiem.ma_loai == ma_loai)

    if ma_tinh:
        query = query.filter(DiaDiem.ma_tinh == ma_tinh)

    if min_price is not None:
        query = query.filter(
            DiaDiem.gia_trung_binh >= min_price
        )

    if max_price is not None:
        query = query.filter(
            DiaDiem.gia_trung_binh <= max_price
        )

    if min_rating is not None:
        query = query.filter(
            DiaDiem.danh_gia >= min_rating
        )

    if keyword:
        query = query.filter(
            DiaDiem.ten.ilike(f"%{keyword}%")
        )

    if tag_ids:
        query = query.filter(
            DiaDiem.thes.any(
                The.ma_the.in_(tag_ids)
            )
        )

    return query.distinct().all()


def get_public_place_detail(
    db,
    ma_dia_diem
):
    return (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.khung_gio_vangs),
            joinedload(DiaDiem.thes)
        )
        .filter(DiaDiem.ma_dia_diem == ma_dia_diem)
        .first()
    )


def filter_dia_diem(
    db: Session,
    loai=None,
    search=None,
    tags=None,
    min_gia=None,
    max_gia=None,
    danh_gia=None
):
    query = (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.thes),
            joinedload(DiaDiem.khung_gio_vangs)
        )
        .join(
            LoaiDiaDiem,
            DiaDiem.ma_loai == LoaiDiaDiem.ma_loai
        )
    )

    if loai:
        query = query.filter(
            LoaiDiaDiem.ten_loai == loai
        )

    if search:
        keywords = search.split()

        for kw in keywords:
            query = query.filter(
                or_(
                    DiaDiem.ten.ilike(f"%{kw}%"),
                    DiaDiem.mo_ta.ilike(f"%{kw}%")
                )
            )

    if tags:
        query = (
            query
            .join(TheDiaDiem)
            .join(The)
            .filter(The.ten_the.in_(tags))
        )

    if min_gia is not None and max_gia is not None:
        query = query.filter(
            DiaDiem.gia_trung_binh.between(
                min_gia,
                max_gia
            )
        )

    if danh_gia is not None:
        query = query.filter(
            DiaDiem.danh_gia >= danh_gia
        )

    return query.distinct().all()


def create(db, dia_diem):
    db.add(dia_diem)
    db.commit()
    db.refresh(dia_diem)
    return dia_diem


def get_by_id(db, id):
    return (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.thes),
            joinedload(DiaDiem.khung_gio_vangs)
        )
        .filter(DiaDiem.ma_dia_diem == id)
        .first()
    )


def get_by_dia_diem(db, ma_dia_diem):
    return (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.thes),
            joinedload(DiaDiem.khung_gio_vangs)
        )
        .filter(DiaDiem.ma_dia_diem == ma_dia_diem)
        .all()
    )


def update(db):
    db.commit()


def delete(db, dia_diem):
    db.delete(dia_diem)
    db.commit()


def get_all(db):
    return (
        db.query(DiaDiem)
        .options(
            joinedload(DiaDiem.tinh),
            joinedload(DiaDiem.loai),
            joinedload(DiaDiem.anh),
            joinedload(DiaDiem.thes),
            joinedload(DiaDiem.khung_gio_vangs)
        )
        .all()
    )