from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    ten_nguoi_dung: str
    email: EmailStr
    mat_khau: str

class UserLogin(BaseModel):
    email: EmailStr
    mat_khau: str

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str
    confirm_password: str

class ForgotPasswordSchema(BaseModel):
    email: EmailStr

class RefreshTokenRequest(BaseModel):
    refresh_token: str