from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db

from app.core.deps import require_role

from app.schemas.khung_gio_vang import (
    KhungGioVangCreate,
    KhungGioVangUpdate
)

from app.services.khung_gio_vang_service import (
    KhungGioVangService
)


router = APIRouter(
    prefix="/khung-gio-vang",
    tags=["Khung giờ vàng"]
)


def serialize_item(item):
    return {
        "ma_khung_gio": item.ma_khung_gio,

        "ma_dia_diem": item.ma_dia_diem,

        "ten_dia_diem": (
            item.dia_diem.ten
            if item.dia_diem
            else None
        ),

        "thang_bat_dau": item.thang_bat_dau,

        "thang_ket_thuc": item.thang_ket_thuc,

        "gio_bat_dau": (
            item.gio_bat_dau.strftime("%H:%M")
            if item.gio_bat_dau
            else None
        ),

        "gio_ket_thuc": (
            item.gio_ket_thuc.strftime("%H:%M")
            if item.gio_ket_thuc
            else None
        ),

        "ngay_ap_dung": item.ngay_ap_dung
    }


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    items = KhungGioVangService.get_all(
        db
    )

    return [
        serialize_item(item)
        for item in items
    ]


@router.get("/{ma_khung_gio}")
def get_by_id(
    ma_khung_gio: UUID,
    db: Session = Depends(get_db)
):
    item = KhungGioVangService.get_by_id(
        db,
        ma_khung_gio
    )

    return serialize_item(
        item
    )


@router.get("/dia-diem/{ma_dia_diem}")
def get_by_dia_diem(
    ma_dia_diem: UUID,
    db: Session = Depends(get_db)
):
    items = KhungGioVangService.get_by_dia_diem(
        db,
        ma_dia_diem
    )

    return [
        serialize_item(item)
        for item in items
    ]


@router.post("")
def create(
    data: KhungGioVangCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    item = KhungGioVangService.create(
        db,
        data
    )

    return serialize_item(
        item
    )


@router.put("/{ma_khung_gio}")
def update(
    ma_khung_gio: UUID,
    data: KhungGioVangUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    item = KhungGioVangService.update(
        db,
        ma_khung_gio,
        data
    )

    return serialize_item(
        item
    )


@router.delete("/{ma_khung_gio}")
def delete(
    ma_khung_gio: UUID,
    db: Session = Depends(get_db),
    admin=Depends(require_role("admin"))
):
    return KhungGioVangService.delete(
        db,
        ma_khung_gio
    )