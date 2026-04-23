import uuid, os
from io import BytesIO
from datetime import time
from fastapi import HTTPException, UploadFile
from PIL import Image
import re

from app.models.dia_diem import DiaDiem
from app.models.tinh import Tinh
from app.models.anh_dia_diem import AnhDiaDiem
from app.models.loai_dia_diem import LoaiDiaDiem 
from app.repositories import dia_diem_repo, anh_repo, yeu_thich_repo
from app.core.config import settings
from app.utils.save_image import save_image,slugify

class DiaDiemService:

    def get_dia_diem_list(db, current_user=None, **filters):
        data = dia_diem_repo.filter_dia_diem(db, **filters)

        favorite_ids = []

        if current_user:
            favs = yeu_thich_repo.get_favorite_ids(
                db,
                current_user.ma_nguoi_dung  
            )
            favorite_ids = [f for f in favs]

        result = []

        for item in data:
            result.append({
                "ma_dia_diem": str(item.ma_dia_diem),
                "ten": item.ten,
                "danh_gia": item.danh_gia,
                "gia_trung_binh": item.gia_trung_binh,
                "is_favorite": item.ma_dia_diem in favorite_ids
            })

        return result

    async def create(
        self,
        db,
        ten,
        ma_tinh,
        ma_loai,
        dia_chi,
        mo_ta=None,
        kinh_do=None,
        vi_do=None,
        gia_trung_binh=None,
        gio_mo=None,
        gio_dong=None,
        website=None,
        sdt=None,
        anh_chinh=None,
        anh_phu=None
    ):
        # 🔥 default giờ
        # gio_mo = gio_mo or time(0, 0)
        # gio_dong = gio_dong or time(23, 59)
        
        if gio_mo is not None:
           gio_mo = gio_mo or time(0, 0)

        if gio_dong is not None:
            gio_dong = gio_dong or time(23, 59)

        if gio_mo and gio_dong:
            if gio_mo >= gio_dong:
                raise HTTPException(400, "Giờ không hợp lệ")
        # 🔥 check tỉnh
        tinh = db.query(Tinh).filter(Tinh.ma_tinh == ma_tinh).first()
        if not tinh:
            raise HTTPException(400, "Tỉnh không hợp lệ")

        # 🔥 check loại
        loai = db.query(LoaiDiaDiem).filter(LoaiDiaDiem.ma_loai == ma_loai).first()
        if not loai:
            raise HTTPException(400, "Loại không hợp lệ")
        
        if not sdt:
            raise HTTPException(400, "Vui lòng nhập số điện thoại")
        
        if not re.match(r"^0\d{9}$", sdt):
            raise HTTPException(
                status_code=400,
                detail="Số điện thoại phải gồm 10 số và bắt đầu bằng 0"
            )
        
        if mo_ta:
            word_count = len(mo_ta.strip().split())
            if word_count > 100:
                raise HTTPException(
                    status_code=400,
                    detail="Mô tả không được vượt quá 100 từ"
                )
            
        # 🔥 tạo địa điểm
        dia_diem = DiaDiem(
            ten=ten,
            ma_tinh=ma_tinh,
            ma_loai=ma_loai,
            dia_chi=dia_chi,
            mo_ta=mo_ta,
            kinh_do=kinh_do,
            vi_do=vi_do,
            gia_trung_binh=gia_trung_binh,
            gio_mo=gio_mo,
            gio_dong=gio_dong,
            website=website,
            sdt=sdt
        )

        dia_diem = dia_diem_repo.create(db, dia_diem)

        #  slug
        tinh_slug = slugify(tinh.ten_tinh, separator="_")
        loai_slug = slugify(loai.ten_loai, separator="_")
        ten_slug = slugify(ten, separator="_")

        # folder thật
        folder = os.path.join(
            settings.UPLOAD_FOLDER,
            tinh_slug,
            loai_slug,
            ten_slug
        )

        os.makedirs(folder, exist_ok=True)

        # ======================
        # 🖼 ẢNH CHÍNH
        # ======================
        if anh_chinh:
            filename = await save_image(anh_chinh, folder)

            db.add(AnhDiaDiem(
                ma_dia_diem=dia_diem.ma_dia_diem,
                url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                la_anh_chinh=True
            ))

        # ======================
        # 🖼 ẢNH PHỤ
        # ======================
        if anh_phu:
            for img in anh_phu:
                filename = await save_image(img, folder)

                db.add(AnhDiaDiem(
                    ma_dia_diem=dia_diem.ma_dia_diem,
                    url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                    la_anh_chinh=False
                ))

        db.commit()    

        return {"id": str(dia_diem.ma_dia_diem)}

    # ================= UPDATE =================
    async def update(
        self,
        db,
        dia_diem_id,
        ten=None,
        dia_chi=None,
        mo_ta=None,
        kinh_do=None,
        ma_tinh=None,
        ma_loai=None,
        vi_do=None,
        gia_trung_binh=None,
        gio_mo=None,
        gio_dong=None,
        website=None,
        sdt=None,
        anh_chinh=None,
        anh_phu=None
    ):
        dia_diem = dia_diem_repo.get_by_id(db, dia_diem_id)

        if not dia_diem:
            raise HTTPException(404, "Không tìm thấy")

        # ======================
        # 🔥 UPDATE FIELD
        # ======================
        if ten is not None:
            dia_diem.ten = ten

        if dia_chi is not None:
            dia_diem.dia_chi = dia_chi

        if mo_ta is not None:
            if len(mo_ta.split()) > 100:
                raise HTTPException(400, "Mô tả quá dài")
            dia_diem.mo_ta = mo_ta

        if kinh_do is not None:
            dia_diem.kinh_do = kinh_do

        if vi_do is not None:
            dia_diem.vi_do = vi_do

        if gia_trung_binh is not None:
            dia_diem.gia_trung_binh = gia_trung_binh

        if website is not None:
            dia_diem.website = website

        if sdt is not None:
            if not re.match(r"^0\d{9}$", sdt):
                raise HTTPException(400, "SĐT không hợp lệ")
            dia_diem.sdt = sdt

        # ======================
        # ⏰ GIỜ
        # ======================
        if gio_mo is not None:
            dia_diem.gio_mo = gio_mo

        if gio_dong is not None:
            dia_diem.gio_dong = gio_dong

        if dia_diem.gio_mo and dia_diem.gio_dong:
            if dia_diem.gio_mo >= dia_diem.gio_dong:
                raise HTTPException(400, "Giờ không hợp lệ")

        # ======================
        # 🌍 UPDATE TỈNH / LOẠI
        # ======================
        if ma_tinh is not None:
            tinh = db.query(Tinh).filter(Tinh.ma_tinh == ma_tinh).first()
            if not tinh:
                raise HTTPException(400, "Tỉnh không hợp lệ")
            dia_diem.ma_tinh = ma_tinh
        else:
            tinh = dia_diem.tinh

        if ma_loai is not None:
            loai = db.query(LoaiDiaDiem).filter(LoaiDiaDiem.ma_loai == ma_loai).first()
            if not loai:
                raise HTTPException(400, "Loại không hợp lệ")
            dia_diem.ma_loai = ma_loai
        else:
            loai = dia_diem.loai

        # ======================
        # 📁 FOLDER
        # ======================
        tinh_slug = slugify(tinh.ten_tinh, separator="_")
        loai_slug = slugify(loai.ten_loai, separator="_")
        ten_slug = slugify(dia_diem.ten, separator="_")

        folder = os.path.join(
            settings.UPLOAD_FOLDER,
            tinh_slug,
            loai_slug,
            ten_slug
        )

        os.makedirs(folder, exist_ok=True)

        # ======================
        # 🖼 ẢNH CHÍNH
        # ======================
        if anh_chinh is not None:
            # 🔥 xoá ảnh chính cũ
            db.query(AnhDiaDiem).filter(
                AnhDiaDiem.ma_dia_diem == dia_diem_id,
                AnhDiaDiem.la_anh_chinh == True
            ).delete()

            filename = await save_image(anh_chinh, folder)

            db.add(AnhDiaDiem(
                ma_dia_diem=dia_diem_id,
                url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                la_anh_chinh=True
            ))

        # ======================
        # 🖼 ẢNH PHỤ
        # ======================
        if anh_phu is not None:
            for img in anh_phu:
                if img:
                    filename = await save_image(img, folder)

                    db.add(AnhDiaDiem(
                        ma_dia_diem=dia_diem_id,
                        url=f"/uploads/{tinh_slug}/{loai_slug}/{ten_slug}/{filename}",
                        la_anh_chinh=False
                    ))

        db.commit()
        db.refresh(dia_diem)

        return {
            "message": "Cập nhật thành công",
            "id": str(dia_diem.ma_dia_diem)
        }
    # # ================= DELETE =================
    def delete(self, db, dia_diem_id):

        dia_diem = dia_diem_repo.get_by_id(db, dia_diem_id)

        if not dia_diem:
            raise HTTPException(404, "Không tìm thấy")

        dia_diem_repo.delete(db, dia_diem)

        return {"message": "deleted"}

    # # ================= GET =================
    def get_by_id(self, db, dia_diem_id):
        dia_diem = dia_diem_repo.get_by_id(db, dia_diem_id)

        if not dia_diem:
            raise HTTPException(404, "Không tìm thấy")

        return dia_diem

    def get_all(self, db):
        return dia_diem_repo.get_all(db)

    # # ================= HELPER =================
    async def _save_images(self, db, ma_dia_diem, images):

        filenames = []
        os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

        for img in images:
            contents = await img.read()
            image = Image.open(BytesIO(contents)).convert("RGB")

            filename = f"dd_{uuid.uuid4().hex}.jpg"
            path = os.path.join(settings.UPLOAD_FOLDER, filename)

            image.save(path, "JPEG")
            filenames.append(filename)

        anh_repo.add_images(db, ma_dia_diem, filenames)