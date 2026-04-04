from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas.user import UserCreate
from app.services.auth_service import register_user
from app.db.session import get_db

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        new_user = register_user(db,user.ten_nguoi_dung, user.email, user.mat_khau)
        return {
            "id": new_user.ma_nguoi_dung,
            "ten_nguoi_dung": new_user.ten_nguoi_dung,
            "email": new_user.email,

        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))