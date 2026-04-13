from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.services.auth_service import AuthService
from app.schemas.user import UserCreate, UserLogin, ForgotPasswordSchema, ResetPasswordSchema, RefreshTokenRequest
from app.db.session import get_db
from app.utils.email import send_reset_email
from app.core.deps import get_current_user, require_role
from fastapi.security import OAuth2PasswordRequestForm

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
# @router.post("/login")
# def login(data: UserLogin, db: Session = Depends(get_db)):
#     try:
#         auth_service = AuthService()

#         access_token, refresh_token, expire = auth_service.login(
#             db=db,
#             email=data.email,
#             mat_khau=data.mat_khau
#         )

#         return {
#             "access_token": access_token,
#             "refresh_token": refresh_token
#         }

#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

#     except Exception:
#         raise HTTPException(status_code=500, detail="Internal server error")
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    auth_service = AuthService()

    if not form_data.username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email không được để trống"
        )

    if not form_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mật khẩu không được để trống"
        )

    try:
        return auth_service.login(
            db=db,
            email=form_data.username,
            mat_khau=form_data.password
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )

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

@router.post("/refresh-token")
def refresh_token(
    data: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    auth_service = AuthService()
    return auth_service.refresh_token(
        db=db,
        refresh_token=data.refresh_token
    )

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

@router.get("/admin")
def admin_api(
    user = Depends(require_role("admin"))
):
    return {"message": "Hello admin"}

@router.put("/me")
async def update_me(
    ten_nguoi_dung: str = Form(None),
    sdt: str = Form(None),
    dia_chi: str = Form(None),
    anh_url: UploadFile = File(None),

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    auth_service = AuthService()

    return await auth_service.update_profile(
        db=db,
        user_id=current_user.ma_nguoi_dung,
        ten_nguoi_dung=ten_nguoi_dung,
        sdt=sdt,
        dia_chi=dia_chi,
        anh=anh_url
    )

@router.put("/me/changepassword")
def change_password(
    current_password: str = Form(...), 
    new_password: str = Form(...), 
    confirm_password: str = Form(...), 

    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    auth_service = AuthService()

    return auth_service.change_password(
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
    auth_service = AuthService()

    return auth_service.logout_all(
        db=db,
        user_id=current_user.ma_nguoi_dung
    )
