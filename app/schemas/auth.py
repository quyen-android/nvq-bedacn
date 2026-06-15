from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    ten_nguoi_dung: str
    email: EmailStr
    mat_khau: str


class ForgotPasswordSchema(BaseModel):
    email: EmailStr


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str
    confirm_password: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class GoogleLoginRequest(BaseModel):
    credential: str