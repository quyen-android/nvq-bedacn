from pydantic import BaseModel,EmailStr

class UserCreate(BaseModel):
    ten_nguoi_dung: str
    email: EmailStr
    mat_khau: str
    

