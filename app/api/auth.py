from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    RefreshTokenRequest
)
from app.db.session import get_db
from app.utils.email import send_reset_email

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        service = AuthService()
        new_user = service.register_user(db, user.ten_nguoi_dung, user.email, user.mat_khau)

        return {
            "id": new_user.ma_nguoi_dung,
            "ten_nguoi_dung": new_user.ten_nguoi_dung,
            "email": new_user.email,
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    service = AuthService()

    if not form_data.username or not form_data.password:
        raise HTTPException(400, "Thiếu email hoặc mật khẩu")

    try:
        return service.login(
            db=db,
            email=form_data.username,
            mat_khau=form_data.password
        )

    except ValueError as e:
        raise HTTPException(401, str(e))
    
@router.post("/forgot-password")
def forgot_password(data: ForgotPasswordSchema, db: Session = Depends(get_db)):
    service = AuthService()
    service.forgot_password(db, data.email)
    return {"msg": "Nếu email tồn tại, đã gửi link"}

@router.post("/reset-password")
def reset_password(data: ResetPasswordSchema, db: Session = Depends(get_db)):
    service = AuthService()
    service.reset_password(db, data.token, data.new_password, data.confirm_password)
    return {"msg": "Đổi mật khẩu thành công"}

@router.post("/refresh-token")
def refresh_token(data: RefreshTokenRequest, db: Session = Depends(get_db)):
    service = AuthService()
    return service.refresh_token(db, data.refresh_token)