from sqlalchemy.orm import Session
from datetime import datetime, timezone
from fastapi import HTTPException
from jose import jwt

from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository
from app.core.security import hash_password, verify_password
from app.core.config import settings
from app.utils.token import create_access_token, create_refresh_token, create_reset_token
from app.utils.email import send_reset_email
from app.core.validator import validate_email,validate_password,validate_required

class AuthService:

    def __init__(self):
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()

    # REGISTER
    def register_user(
        self,
        db: Session,
        ten_nguoi_dung: str,
        email: str,
        mat_khau: str
    ):

        validate_required(
            ten_nguoi_dung,
            "Tên người dùng"
        )

        validate_email(email)

        validate_password(mat_khau)

        if self.user_repo.get_user_by_email(db, email):
            raise HTTPException(
                status_code=400,
                detail="Email đã tồn tại"
            )

        user = self.user_repo.create_user(
            db,
            ten_nguoi_dung,
            email,
            hash_password(mat_khau)
        )

        return user

    # LOGIN
    def login(
        self,
        db: Session,
        email: str,
        mat_khau: str
    ):

        validate_required(email, "Email")

        validate_required(mat_khau, "Mật khẩu")

        user = self.user_repo.get_user_by_email(
            db,
            email
        )

        if not user or not verify_password(
            mat_khau,
            user.mat_khau
        ):
            raise HTTPException(
                status_code=400,
                detail="Email hoặc mật khẩu không đúng"
            )

        if not user.trang_thai:
            raise HTTPException(
                status_code=400,
                detail="Tài khoản bị khóa"
            )

        user.dn_lan_cuoi = datetime.now(
            timezone.utc
        )

        db.commit()

        access = create_access_token({
            "sub": str(user.ma_nguoi_dung)
        })

        refresh, expire = create_refresh_token({
            "sub": str(user.ma_nguoi_dung)
        })

        self.token_repo.create(
            db,
            user.ma_nguoi_dung,
            refresh,
            expire
        )

        return {
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }

    # REFRESH TOKEN
    def refresh_token(
        self,
        db: Session,
        refresh_token: str
    ):

        validate_required(
            refresh_token,
            "Refresh token"
        )

        rt = self.token_repo.get(
            db,
            refresh_token
        )

        if not rt or rt.da_thu_hoi:
            raise HTTPException(
                status_code=400,
                detail="Token không hợp lệ"
            )

        if rt.thoi_gian_het_han < datetime.now(
            timezone.utc
        ):
            raise HTTPException(
                status_code=400,
                detail="Token hết hạn"
            )

        self.token_repo.revoke(
            db,
            refresh_token
        )

        new_access = create_access_token({
            "sub": str(rt.ma_nguoi_dung)
        })

        new_refresh, expire = create_refresh_token({
            "sub": str(rt.ma_nguoi_dung)
        })

        self.token_repo.create(
            db,
            rt.ma_nguoi_dung,
            new_refresh,
            expire
        )

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer"
        }

    # FORGOT PASSWORD
    def forgot_password(
        self,
        db: Session,
        email: str
    ):

        validate_email(email)

        user = self.user_repo.get_user_by_email(
            db,
            email
        )

        if user:
            token = create_reset_token(email)

            reset_link = (
                f"http://localhost:5173"
                f"/reset-password?token={token}"
            )

            send_reset_email(
                email,
                reset_link
            )

        return {
            "message":
            "Nếu email tồn tại, link reset đã được gửi"
        }

    # RESET PASSWORD
    def reset_password(
        self,
        db: Session,
        token: str,
        new_password: str,
        confirm_password: str
    ):

        validate_required(token, "Token")

        validate_password(new_password)

        validate_required(
            confirm_password,
            "Xác nhận mật khẩu"
        )

        if new_password != confirm_password:
            raise HTTPException(
                status_code=400,
                detail="Mật khẩu không trùng nhau"
            )

        try:

            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )

            if payload.get("type") != "reset":
                raise ValueError()

            user = self.user_repo.get_user_by_email(
                db,
                payload.get("sub")
            )

            if not user:
                raise ValueError()

            user.mat_khau = hash_password(
                new_password
            )

            self.token_repo.revoke_all_by_user(
                db,
                user.ma_nguoi_dung
            )

            db.commit()

            return {
                "message":
                "Đổi mật khẩu thành công"
            }

        except:
            raise HTTPException(
                status_code=400,
                detail="Token không hợp lệ hoặc hết hạn"
            )

    # LOGOUT ALL
    def logout_all(
        self,
        db,
        user_id: int
    ):

        self.token_repo.revoke_all_by_user(
            db,
            user_id
        )

        return {
            "message":
            "Đã logout tất cả thiết bị"
        }