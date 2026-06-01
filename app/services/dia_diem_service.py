import os
import re
from datetime import time

from fastapi import HTTPException

from app.core.config import settings
from app.models.anh_dia_diem import AnhDiaDiem
from app.models.dia_diem import DiaDiem
from app.models.loai_dia_diem import LoaiDiaDiem
from app.models.tinh import Tinh
from app.repositories import dia_diem_repo, yeu_thich_repo
from app.services.rag_service import RagService
from app.utils.save_image import save_image, slugify


class DiaDiemService:

    @staticmethod
    def _format_image(img):
        return {
            "ma_anh": str(img.ma_anh),
            "url": img.url,
            "la_anh_chinh": img.la_anh_chinh
        }

    @staticmethod
    def _format_place(item, favorite_ids=None):
        favorite_ids = favorite_ids or []

        anh_chinh = None
        anh_phu = []

        for img in item.anh or []:
            image_data = DiaDiemService._format_image(img)

            if img.la_anh_chinh:
                anh_chinh = image_data
            else:
                anh_phu.append(image_data)

        return {
            "ma_dia_diem": str(item.ma_dia_diem),
            "id": str(item.ma_dia_diem),

            "ten": item.ten,
            "dia_chi": item.dia_chi,
            "mo_ta": item.mo_ta,

            "ma_tinh": str(item.ma_tinh) if item.ma_tinh else "",
            "ma_loai": str(item.ma_loai) if item.ma_loai else "",

            "ten_tinh": item.tinh.ten_tinh if item.tinh else "",
            "ten_loai": item.loai.ten_loai if item.loai else "",

            "kinh_do": item.kinh_do,
            "vi_do": item.vi_do,

            "gia_trung_binh": item.gia_trung_binh,
            "danh_gia": item.danh_gia,
            "so_danh_gia": item.so_danh_gia,

            "gio_mo": str(item.gio_mo) if item.gio_mo else "",
            "gio_dong": str(item.gio_dong) if item.gio_dong else "",

            "website": item.website,
            "sdt": item.sdt,

            "anh_chinh": anh_chinh,
            "anh_phu": anh_phu,
            "anh_dia_diems": anh_phu,
            "images": item.anh and [
                DiaDiemService._format_image(img)
                for img in item.anh
            ] or [],

            "ma_the": [
                str(the.ma_the)
                for the in item.thes
            ] if item.thes else [],

            "tags": [
                {
                    "ma_the": str(the.ma_the),
                    "ten_the": the.ten_the
                }
                for the in item.thes
            ] if item.thes else [],

            "is_favorite": item.ma_dia_diem in favorite_ids
        }

    def get_dia_diem_list(
        db,
        current_user=None,
        **filters
    ):
        data = dia_diem_repo.filter_dia_diem(
            db,
            **filters
        )

        favorite_ids = []

        if current_user:
            favs = yeu_thich_repo.get_favorite_ids(
                db,
                current_user.ma_nguoi_dung
            )

            favorite_ids = [f for f in favs]

        return [
            DiaDiemService._format_place(
                item,
                favorite_ids
            )
            for item in data
        ]

    async def create(
        self,
        db,
        ten,
        ma_tinh,
        ma_loai,
        dia_chi,
        mo_ta,
        kinh_do,
        vi_do,
        gia_trung_binh,
        danh_gia,
        so_danh_gia,
        gio_mo,
        gio_dong,
        website,
        sdt,
        anh_chinh,
        anh_phu
    ):
        gio_mo = self._parse_time(
            gio_mo,
            time(0, 0)
        )

        gio_dong = self._parse_time(
            gio_dong,
            time(23, 59)
        )

        self._validate_required_text(
            ten,
            "Vui lòng nhập tên địa điểm"
        )

        self._validate_phone(sdt)
        self._validate_description(mo_ta)
        self._validate_time(gio_mo, gio_dong)
        self._validate_coordinates(kinh_do, vi_do)

        tinh = db.query(Tinh).filter(
            Tinh.ma_tinh == ma_tinh
        ).first()

        if not tinh:
            raise HTTPException(
                400,
                "Tỉnh không hợp lệ"
            )

        loai = db.query(LoaiDiaDiem).filter(
            LoaiDiaDiem.ma_loai == ma_loai
        ).first()

        if not loai:
            raise HTTPException(
                400,
                "Loại không hợp lệ"
            )

        dia_diem = DiaDiem(
            ten=ten.strip(),
            ma_tinh=ma_tinh,
            ma_loai=ma_loai,
            dia_chi=dia_chi,
            mo_ta=mo_ta,
            kinh_do=kinh_do,
            vi_do=vi_do,
            gia_trung_binh=gia_trung_binh,
            danh_gia=danh_gia if danh_gia is not None else 0,
            so_danh_gia=so_danh_gia if so_danh_gia is not None else 0,
            gio_mo=gio_mo,
            gio_dong=gio_dong,
            website=website,
            sdt=sdt
        )

        dia_diem = dia_diem_repo.create(
            db,
            dia_diem
        )

        folder, tinh_slug, loai_slug, ten_slug = self._build_folder(
            tinh.ten_tinh,
            loai.ten_loai,
            ten
        )

        if anh_chinh:
            await self._save_main_image(
                db=db,
                ma_dia_diem=dia_diem.ma_dia_diem,
                image=anh_chinh,
                folder=folder,
                tinh_slug=tinh_slug,
                loai_slug=loai_slug,
                ten_slug=ten_slug
            )

        if anh_phu:
            await self._save_sub_images(
                db=db,
                ma_dia_diem=dia_diem.ma_dia_diem,
                images=anh_phu,
                folder=folder,
                tinh_slug=tinh_slug,
                loai_slug=loai_slug,
                ten_slug=ten_slug
            )

        db.commit()
        db.refresh(dia_diem)

        RagService.add_place(dia_diem)

        return {
            "id": str(dia_diem.ma_dia_diem),
            "ma_dia_diem": str(dia_diem.ma_dia_diem)
        }

    async def update(
        self,
        db,
        dia_diem_id,
        ten=None,
        dia_chi=None,
        mo_ta=None,
        kinh_do=None,
        vi_do=None,
        ma_tinh=None,
        ma_loai=None,
        gia_trung_binh=None,
        danh_gia=None,
        so_danh_gia=None,
        gio_mo=None,
        gio_dong=None,
        website=None,
        sdt=None,
        anh_chinh=None
    ):
        dia_diem = dia_diem_repo.get_by_id(
            db,
            dia_diem_id
        )

        if not dia_diem:
            raise HTTPException(
                404,
                "Không tìm thấy"
            )

        if gio_mo is not None:
            gio_mo = self._parse_time(gio_mo)

        if gio_dong is not None:
            gio_dong = self._parse_time(gio_dong)

        if ten is not None:
            self._validate_required_text(
                ten,
                "Vui lòng nhập tên địa điểm"
            )

        if sdt is not None:
            self._validate_phone(sdt)

        if mo_ta is not None:
            self._validate_description(mo_ta)

        self._validate_time(
            gio_mo or dia_diem.gio_mo,
            gio_dong or dia_diem.gio_dong
        )

        self._validate_coordinates(
            kinh_do if kinh_do is not None else dia_diem.kinh_do,
            vi_do if vi_do is not None else dia_diem.vi_do
        )

        fields = {
            "ten": ten.strip() if ten is not None else None,
            "dia_chi": dia_chi,
            "mo_ta": mo_ta,
            "kinh_do": kinh_do,
            "vi_do": vi_do,
            "gia_trung_binh": gia_trung_binh,
            "danh_gia": danh_gia,
            "so_danh_gia": so_danh_gia,
            "gio_mo": gio_mo,
            "gio_dong": gio_dong,
            "website": website,
            "sdt": sdt,
        }

        for key, value in fields.items():
            if value is not None:
                setattr(
                    dia_diem,
                    key,
                    value
                )

        if ma_tinh is not None:
            tinh = db.query(Tinh).filter(
                Tinh.ma_tinh == ma_tinh
            ).first()

            if not tinh:
                raise HTTPException(
                    400,
                    "Tỉnh không hợp lệ"
                )

            dia_diem.ma_tinh = ma_tinh
        else:
            tinh = dia_diem.tinh

        if ma_loai is not None:
            loai = db.query(LoaiDiaDiem).filter(
                LoaiDiaDiem.ma_loai == ma_loai
            ).first()

            if not loai:
                raise HTTPException(
                    400,
                    "Loại không hợp lệ"
                )

            dia_diem.ma_loai = ma_loai
        else:
            loai = dia_diem.loai

        folder, tinh_slug, loai_slug, ten_slug = self._build_folder(
            tinh.ten_tinh,
            loai.ten_loai,
            dia_diem.ten
        )

        if anh_chinh is not None:
            await self._delete_main_image(
                db,
                dia_diem_id
            )

            await self._save_main_image(
                db=db,
                ma_dia_diem=dia_diem_id,
                image=anh_chinh,
                folder=folder,
                tinh_slug=tinh_slug,
                loai_slug=loai_slug,
                ten_slug=ten_slug
            )

        db.commit()
        db.refresh(dia_diem)

        RagService.update_place(dia_diem)

        return {
            "message": "Cập nhật thành công",
            "id": str(dia_diem.ma_dia_diem),
            "ma_dia_diem": str(dia_diem.ma_dia_diem)
        }

    async def add_sub_images(
        self,
        db,
        dia_diem_id,
        anh_phu
    ):
        dia_diem = dia_diem_repo.get_by_id(
            db,
            dia_diem_id
        )

        if not dia_diem:
            raise HTTPException(
                404,
                "Không tìm thấy địa điểm"
            )

        tinh = dia_diem.tinh
        loai = dia_diem.loai

        if not tinh or not loai:
            raise HTTPException(
                400,
                "Địa điểm thiếu tỉnh hoặc loại"
            )

        folder, tinh_slug, loai_slug, ten_slug = self._build_folder(
            tinh.ten_tinh,
            loai.ten_loai,
            dia_diem.ten
        )

        await self._save_sub_images(
            db=db,
            ma_dia_diem=dia_diem_id,
            images=anh_phu,
            folder=folder,
            tinh_slug=tinh_slug,
            loai_slug=loai_slug,
            ten_slug=ten_slug
        )

        db.commit()

        return {
            "message": "Thêm ảnh phụ thành công"
        }

    def delete_sub_image(
        self,
        db,
        ma_anh
    ):
        image = db.query(AnhDiaDiem).filter(
            AnhDiaDiem.ma_anh == ma_anh,
            AnhDiaDiem.la_anh_chinh == False
        ).first()

        if not image:
            raise HTTPException(
                404,
                "Không tìm thấy ảnh phụ"
            )

        self._remove_physical_file(image.url)

        db.delete(image)
        db.commit()

        return {
            "message": "Xóa ảnh phụ thành công"
        }

    def delete(
        self,
        db,
        dia_diem_id
    ):
        dia_diem = dia_diem_repo.get_by_id(
            db,
            dia_diem_id
        )

        if not dia_diem:
            raise HTTPException(
                404,
                "Không tìm thấy"
            )

        images = db.query(AnhDiaDiem).filter(
            AnhDiaDiem.ma_dia_diem == dia_diem_id
        ).all()

        for img in images:
            self._remove_physical_file(img.url)

        dia_diem_repo.delete(
            db,
            dia_diem
        )

        RagService.delete_place(dia_diem_id)

        return {
            "message": "deleted"
        }

    def get_by_id(
        self,
        db,
        dia_diem_id
    ):
        dia_diem = dia_diem_repo.get_by_id(
            db,
            dia_diem_id
        )

        if not dia_diem:
            raise HTTPException(
                404,
                "Không tìm thấy"
            )

        return self._format_place(dia_diem)

    def get_all(
        self,
        db
    ):
        data = dia_diem_repo.get_all(db)

        return [
            self._format_place(item)
            for item in data
        ]

    def _parse_time(
        self,
        value,
        default_value=None
    ):
        if not value:
            return default_value

        if isinstance(value, time):
            return value

        try:
            hour, minute = str(value).split(":")[:2]

            return time(
                int(hour),
                int(minute)
            )
        except Exception:
            raise HTTPException(
                400,
                "Giờ không hợp lệ"
            )

    def _validate_required_text(
        self,
        value,
        message
    ):
        if not value or not value.strip():
            raise HTTPException(
                400,
                message
            )

    def _validate_coordinates(
        self,
        kinh_do,
        vi_do
    ):
        if kinh_do is not None:
            kinh_do = float(kinh_do)

            if kinh_do < -180 or kinh_do > 180:
                raise HTTPException(
                    400,
                    "Kinh độ phải từ -180 đến 180"
                )

        if vi_do is not None:
            vi_do = float(vi_do)

            if vi_do < -90 or vi_do > 90:
                raise HTTPException(
                    400,
                    "Vĩ độ phải từ -90 đến 90"
                )

    def _validate_phone(
        self,
        sdt
    ):
        if not sdt:
            raise HTTPException(
                400,
                "Vui lòng nhập số điện thoại"
            )

        if not re.match(
            r"^0\d{9}$",
            sdt
        ):
            raise HTTPException(
                400,
                "Số điện thoại không hợp lệ"
            )

    def _validate_description(
        self,
        mo_ta
    ):
        if not mo_ta:
            return

        if len(mo_ta.strip().split()) > 100:
            raise HTTPException(
                400,
                "Mô tả không được vượt quá 100 từ"
            )

    def _validate_time(
        self,
        gio_mo,
        gio_dong
    ):
        if gio_mo and gio_dong and gio_mo >= gio_dong:
            raise HTTPException(
                400,
                "Giờ không hợp lệ"
            )

    def _build_folder(
        self,
        tinh,
        loai,
        ten
    ):
        tinh_slug = slugify(
            tinh,
            separator="_"
        )

        loai_slug = slugify(
            loai,
            separator="_"
        )

        ten_slug = slugify(
            ten,
            separator="_"
        )

        folder = os.path.join(
            settings.UPLOAD_FOLDER,
            tinh_slug,
            loai_slug,
            ten_slug
        )

        os.makedirs(
            folder,
            exist_ok=True
        )

        return (
            folder,
            tinh_slug,
            loai_slug,
            ten_slug
        )

    async def _save_main_image(
        self,
        db,
        ma_dia_diem,
        image,
        folder,
        tinh_slug,
        loai_slug,
        ten_slug
    ):
        filename = await save_image(
            image,
            folder
        )

        db.add(
            AnhDiaDiem(
                ma_dia_diem=ma_dia_diem,
                url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                la_anh_chinh=True
            )
        )

    async def _save_sub_images(
        self,
        db,
        ma_dia_diem,
        images,
        folder,
        tinh_slug,
        loai_slug,
        ten_slug
    ):
        for img in images:
            if not img:
                continue

            filename = await save_image(
                img,
                folder
            )

            db.add(
                AnhDiaDiem(
                    ma_dia_diem=ma_dia_diem,
                    url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                    la_anh_chinh=False
                )
            )

    async def _delete_main_image(
        self,
        db,
        ma_dia_diem
    ):
        old_main = db.query(AnhDiaDiem).filter(
            AnhDiaDiem.ma_dia_diem == ma_dia_diem,
            AnhDiaDiem.la_anh_chinh == True
        ).first()

        if not old_main:
            return

        self._remove_physical_file(old_main.url)

        db.delete(old_main)

    async def _delete_sub_images(
        self,
        db,
        ma_dia_diem
    ):
        old_images = db.query(AnhDiaDiem).filter(
            AnhDiaDiem.ma_dia_diem == ma_dia_diem,
            AnhDiaDiem.la_anh_chinh == False
        ).all()

        for old in old_images:
            self._remove_physical_file(old.url)
            db.delete(old)

    def _remove_physical_file(
        self,
        image_url
    ):
        file_path = image_url.replace(
            "/uploads/",
            f"{settings.UPLOAD_FOLDER}/"
        )

        if os.path.exists(file_path):
            os.remove(file_path)