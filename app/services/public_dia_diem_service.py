from fastapi import HTTPException

from app.repositories import (
    dia_diem_repo,
    yeu_thich_repo
)


class PublicDiaDiemService:

    def get_places(
        self,
        db,
        current_user=None,
        ma_loai=None,
        ma_tinh=None,
        min_price=None,
        max_price=None,
        min_rating=None,
        tag_ids=None,
        keyword=None
    ):
        places = dia_diem_repo.filter_public_places(
            db=db,
            ma_loai=ma_loai,
            ma_tinh=ma_tinh,
            min_price=min_price,
            max_price=max_price,
            min_rating=min_rating,
            tag_ids=tag_ids,
            keyword=keyword
        )

        favorite_ids = self._get_favorite_ids(
            db,
            current_user
        )

        return [
            self._to_basic_response(
                place,
                favorite_ids
            )
            for place in places
        ]

    def get_place_detail(
        self,
        db,
        ma_dia_diem,
        current_user=None
    ):
        place = dia_diem_repo.get_public_place_detail(
            db,
            ma_dia_diem
        )

        if not place:
            raise HTTPException(
                status_code=404,
                detail="Không tìm thấy địa điểm"
            )

        favorite_ids = self._get_favorite_ids(
            db,
            current_user
        )

        return self._to_detail_response(
            place,
            favorite_ids
        )

    def _get_favorite_ids(
        self,
        db,
        current_user
    ):
        if not current_user:
            return []

        favorite_ids = yeu_thich_repo.get_favorite_ids(
            db,
            current_user.ma_nguoi_dung
        )

        return [
            str(item)
            for item in favorite_ids
        ]

    def _get_main_image(
        self,
        place
    ):
        images = getattr(
            place,
            "anh",
            []
        )

        main_image = next(
            (
                img for img in images
                if img.la_anh_chinh
            ),
            None
        )

        if main_image:
            return {
                "ma_anh": str(main_image.ma_anh),
                "url": main_image.url,
                "la_anh_chinh": main_image.la_anh_chinh
            }

        if images:
            img = images[0]

            return {
                "ma_anh": str(img.ma_anh),
                "url": img.url,
                "la_anh_chinh": img.la_anh_chinh
            }

        return None

    def _to_basic_response(
        self,
        place,
        favorite_ids
    ):
        main_image = self._get_main_image(place)

        images = getattr(
            place,
            "anh",
            []
        )

        return {
            "ma_dia_diem": str(place.ma_dia_diem),
            "ten": place.ten,
            "dia_chi": place.dia_chi,
            "gia_trung_binh": float(place.gia_trung_binh) if place.gia_trung_binh is not None else 0,
            "danh_gia": float(place.danh_gia) if place.danh_gia is not None else 0,
            "so_danh_gia": place.so_danh_gia or 0,
            "gio_mo": str(place.gio_mo) if place.gio_mo else None,
            "gio_dong": str(place.gio_dong) if place.gio_dong else None,

            "anh_chinh": main_image,

            "anh": [
                {
                    "ma_anh": str(img.ma_anh),
                    "url": img.url,
                    "la_anh_chinh": img.la_anh_chinh
                }
                for img in images
            ],

            "tinh": {
                "ma_tinh": str(place.tinh.ma_tinh),
                "ten_tinh": place.tinh.ten_tinh
            } if place.tinh else None,

            "loai": {
                "ma_loai": str(place.loai.ma_loai),
                "ten_loai": place.loai.ten_loai
            } if place.loai else None,

            "is_favorite": str(place.ma_dia_diem) in favorite_ids
        }

    def _to_detail_response(
        self,
        place,
        favorite_ids
    ):
        images = getattr(
            place,
            "anh",
            []
        )

        tags = getattr(
            place,
            "thes",
            []
        )

        golden_hours = getattr(
            place,
            "khung_gio_vangs",
            []
        )

        return {
            "ma_dia_diem": str(place.ma_dia_diem),
            "ten": place.ten,
            "dia_chi": place.dia_chi,
            "mo_ta": place.mo_ta,
            "kinh_do": float(place.kinh_do) if place.kinh_do is not None else None,
            "vi_do": float(place.vi_do) if place.vi_do is not None else None,
            "gia_trung_binh": float(place.gia_trung_binh) if place.gia_trung_binh is not None else 0,
            "danh_gia": float(place.danh_gia) if place.danh_gia is not None else 0,
            "so_danh_gia": place.so_danh_gia or 0,
            "gio_mo": str(place.gio_mo) if place.gio_mo else None,
            "gio_dong": str(place.gio_dong) if place.gio_dong else None,
            "website": place.website,
            "sdt": place.sdt,

            "tinh": {
                "ma_tinh": str(place.tinh.ma_tinh),
                "ten_tinh": place.tinh.ten_tinh
            } if place.tinh else None,

            "loai": {
                "ma_loai": str(place.loai.ma_loai),
                "ten_loai": place.loai.ten_loai
            } if place.loai else None,

            "anh": [
                {
                    "ma_anh": str(img.ma_anh),
                    "url": img.url,
                    "la_anh_chinh": img.la_anh_chinh
                }
                for img in images
            ],

            "the": [
                {
                    "ma_the": str(tag.ma_the),
                    "ten_the": tag.ten_the
                }
                for tag in tags
            ],

            "khung_gio_vang": [
                {
                    "ma_khung_gio": str(item.ma_khung_gio),
                    "thang_bat_dau": item.thang_bat_dau,
                    "thang_ket_thuc": item.thang_ket_thuc,
                    "gio_bat_dau": str(item.gio_bat_dau) if item.gio_bat_dau else None,
                    "gio_ket_thuc": str(item.gio_ket_thuc) if item.gio_ket_thuc else None
                }
                for item in golden_hours
            ],

            "is_favorite": str(place.ma_dia_diem) in favorite_ids
        }