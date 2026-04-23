import uuid, os
from io import BytesIO
from typing import Optional
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from PIL import Image

from app.repositories.user_repo import UserRepository
from app.core.config import settings
from app.core.validator import validate_phone


class UserService:

    def __init__(self):
        self.user_repo = UserRepository()

    async def update_profile(
        self,
        db: Session,
        user_id: uuid.UUID,
        ten_nguoi_dung: Optional[str] = None,
        sdt: Optional[str] = None,
        dia_chi: Optional[str] = None,
        anh: Optional[UploadFile] = None
    ):
        user = self.user_repo.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(404, "User không tồn tại")

        updated = False

        if ten_nguoi_dung is not None:
            user.ten_nguoi_dung = ten_nguoi_dung
            updated = True

        if sdt is not None:
            validate_phone(sdt)

            existing = self.user_repo.get_user_by_sdt(db, sdt)
            if existing and existing.ma_nguoi_dung != user_id:
                raise HTTPException(400, "SĐT đã tồn tại")

            user.sdt = sdt
            updated = True

        if dia_chi is not None:
            user.dia_chi = dia_chi
            updated = True

        if anh:
            contents = await anh.read()

            image = Image.open(BytesIO(contents)).convert("RGB")

            os.makedirs(settings.UPLOAD_FOLDER, exist_ok=True)

            filename = f"user_{user_id}_{uuid.uuid4().hex}.jpg"
            filepath = os.path.join(settings.UPLOAD_FOLDER, "users", filename)

            image.save(filepath, "JPEG")

            user.anh_url = filename
            updated = True

        if not updated:
            return {"message": "Không có dữ liệu thay đổi"}

        db.commit()
        db.refresh(user)

        return {"message": "Cập nhật thành công"}