from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, ForgotPasswordSchema, ResetPasswordSchema
from app.db.session import get_db
from app.utils.email import send_reset_email

router = APIRouter(prefix="/auth", tags=["Auth"])


# REGISTER
@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService()

        new_user = auth_service.register_user(
            db,
            user.ten_nguoi_dung,
            user.email,
            user.mat_khau
        )

        return {
            "id": new_user.ma_nguoi_dung,
            "ten_nguoi_dung": new_user.ten_nguoi_dung,
            "email": new_user.email,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# LOGIN
@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService()

        access_token, refresh_token, expire = auth_service.login(
            db=db,
            email=data.email,
            mat_khau=data.mat_khau
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")
    
# FORGOT PASSWORD
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    try:
        service = AuthService()
        service.forgot_password(db, data.email)

        return {"msg": "Nếu email tồn tại, chúng tôi đã gửi link"}

    except Exception:
        raise HTTPException(status_code=500, detail="Internal server error")


#  RESET PASSWORD
@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    try:
        service = AuthService()
        service.reset_password(db, data.token, data.new_password, data.confirm_password)
        
        return {"msg": "Đổi mật khẩu thành công"}

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.get("/test-email")
def test_email():
    send_reset_email(
        "quyen24a3k49@gmail.com",
        "http://localhost:3000/reset-password?token=abc"
    )
    return {"msg": "Check mail đi "}