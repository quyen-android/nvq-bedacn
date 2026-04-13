from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.services.user_service import UserService
from app.services.auth_service import AuthService
from app.services.password_service import PasswordService
from app.db.session import get_db
from app.core.deps import get_current_user, require_role

router = APIRouter(prefix="/users", tags=["User"])

@router.get("/me")
def get_me(current_user = Depends(get_current_user)):
    return {
        "id": current_user.ma_nguoi_dung,
        "ten_nguoi_dung": current_user.ten_nguoi_dung,
        "email": current_user.email,
        "sdt": current_user.sdt,
        "dia_chi": current_user.dia_chi,
        "anh_url": current_user.anh_url
    }

@router.put("/me")
async def update_me(
    ten_nguoi_dung: str = Form(None),
    sdt: str = Form(None),
    dia_chi: str = Form(None),
    anh: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = UserService()

    return await service.update_profile(
        db=db,
        user_id=current_user.ma_nguoi_dung,
        ten_nguoi_dung=ten_nguoi_dung,
        sdt=sdt,
        dia_chi=dia_chi,
        anh=anh
    )

@router.put("/me/change-password")
def change_password(
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = PasswordService()

    return service.change_password(
        db=db,
        user_id=current_user.ma_nguoi_dung,
        current_password=current_password.strip(),
        new_password=new_password.strip(),
        confirm_password=confirm_password.strip()
    )

@router.post("/logout-all")
def logout_all(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    service = AuthService()

    return service.logout_all(db, current_user.ma_nguoi_dung)

@router.get("/admin")
def admin_api(user = Depends(require_role("admin"))):
    return {"message": "Hello admin"}

