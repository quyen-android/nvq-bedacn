from sqlalchemy.orm import Session
from datetime import datetime,timezone
from jose import jwt

from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository
from app.core.security import hash_password, verify_password
from app.utils.token import create_access_token, create_refresh_token, create_reset_token
from app.utils.email import send_reset_email
from app.core.security import settings

class AuthService:

    def __init__(self):
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()

    # 🔹 REGISTER
    def register_user(self, db: Session, ten_nguoi_dung: str, email: str, mat_khau: str):

        existing_user = self.user_repo.get_user_by_email(db, email)

        if existing_user:
            raise ValueError("Email already exists")

        hashed_password = hash_password(mat_khau)

        user = self.user_repo.create_user(
            db,
            ten_nguoi_dung,
            email,
            hashed_password
        )

        return user

    # LOGIN
    def login(self, db: Session, email: str, mat_khau: str):

        user = self.user_repo.get_user_by_email(db, email)

        if not user:
            raise ValueError("Email hoặc mật khẩu không đúng")

        if not verify_password(mat_khau, user.mat_khau):
            raise ValueError("Email hoặc mật khẩu không đúng")

        if user.trang_thai != True:
            raise ValueError("Tài khoản bị khóa")
    
        user.dn_lan_cuoi = datetime.now(timezone.utc)
        db.commit()

        access = create_access_token({"sub": str(user.ma_nguoi_dung),})
        refresh,expire = create_refresh_token({"sub": str(user.ma_nguoi_dung)})

        self.token_repo.create(
            db=db,
            ma_nguoi_dung=user.ma_nguoi_dung,
            ma_token=refresh,
            thoi_gian_het_han=expire
        )

        return{
            "access_token": access,
            "refresh_token": refresh,
            "token_type": "bearer"
        }

    # REFRESH TOKEN
    def refresh_token(self, db: Session, refresh_token: str):

        rt = self.token_repo.get(db, refresh_token)

        if not rt:
            raise ValueError("Token không tồn tại")

        if rt.da_thu_hoi:
            raise ValueError("Token đã bị thu hồi")

        if rt.thoi_gian_het_han < datetime.now(timezone.utc):
            raise ValueError("Token hết hạn")

        self.token_repo.revoke(db, refresh_token)

        new_access = create_access_token({"sub": str(rt.ma_nguoi_dung)})
        new_refresh, expire = create_refresh_token({"sub": str(rt.ma_nguoi_dung)})

        self.token_repo.create(
            db=db,
            ma_nguoi_dung=rt.ma_nguoi_dung,
            ma_token=new_refresh,
            thoi_gian_het_han=expire
        )

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
            "token_type": "bearer"
        }
        
    # FORGOT MẬT KHẨU
    def forgot_password(self, db: Session, email: str):

        user = self.user_repo.get_user_by_email(db, email)

        if not user:
            return {"message": "Nếu email tồn tại, link reset đã được gửi"}

        token = create_reset_token(email)

        reset_link = f"http://localhost:3000/reset-password?token={token}"

        send_reset_email(email, reset_link)

        return {"message": "Nếu email tồn tại, link reset đã được gửi"}

    # RESET MẬT KHẨU
    def reset_password(self, db: Session, token: str, new_password: str, confirm_password: str):

        if new_password != confirm_password:
            raise ValueError("Mật khẩu không trùng nhau")
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=settings.ALGORITHM
            )

            if payload.get("type") != "reset":
                raise ValueError("Token không hợp lệ")

            email = payload.get("sub")

            user = self.user_repo.get_user_by_email(db, email)
            
            if not user:
                raise ValueError("User không tồn tại")

            user.mat_khau = hash_password(new_password)

            self.token_repo.revoke_all_by_user(db, user.ma_nguoi_dung)

            db.commit()

        except Exception:
            raise ValueError("Token không hợp lệ hoặc hết hạn")