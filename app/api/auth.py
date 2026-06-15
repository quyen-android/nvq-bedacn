from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from app.services.auth_service import AuthService
from app.schemas.auth import (
    UserCreate,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    RefreshTokenRequest,
    GoogleLoginRequest
)
from app.db.session import get_db


router = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)


@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    service = AuthService()

    new_user = service.register_user(
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


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    service = AuthService()

    if not form_data.username or not form_data.password:
        raise HTTPException(
            status_code=400,
            detail="Thiếu email hoặc mật khẩu"
        )

    return service.login(
        db=db,
        email=form_data.username,
        mat_khau=form_data.password
    )


@router.post("/google")
def google_login(
    data: GoogleLoginRequest,
    db: Session = Depends(get_db)
):
    service = AuthService()

    return service.login_google(
        db=db,
        credential=data.credential
    )


@router.post("/forgot-password")
def forgot_password(
    data: ForgotPasswordSchema,
    db: Session = Depends(get_db)
):
    service = AuthService()

    service.forgot_password(
        db,
        data.email
    )

    return {
        "msg": "Nếu email tồn tại, đã gửi link"
    }


@router.post("/reset-password")
def reset_password(
    data: ResetPasswordSchema,
    db: Session = Depends(get_db)
):
    service = AuthService()

    service.reset_password(
        db,
        data.token,
        data.new_password,
        data.confirm_password
    )

    return {
        "msg": "Đổi mật khẩu thành công"
    }


@router.post("/refresh-token")
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    service = AuthService()

    return service.refresh_token(
        db,
        data.refresh_token
    )