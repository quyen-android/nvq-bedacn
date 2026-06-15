from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/admin/tai-khoan",
    tags=["Admin - Tài khoản"]
)


def check_admin(current_user):
    if current_user.quyen != "admin":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập"
        )


def serialize_user(user):
    return {
        "ma_nguoi_dung": str(user.ma_nguoi_dung),
        "ten_nguoi_dung": user.ten_nguoi_dung,
        "email": user.email,
        "sdt": getattr(user, "sdt", None),
        "dia_chi": getattr(user, "dia_chi", None),
        "anh_url": getattr(user, "anh_url", None),
        "quyen": user.quyen,
        "trang_thai": getattr(user, "trang_thai", True),
        "ngay_tao": getattr(user, "ngay_tao", None),
    }


@router.get("")
def get_users(
    keyword: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    query = db.query(User)

    if keyword:
        like = f"%{keyword}%"

        query = query.filter(
            or_(
                User.ten_nguoi_dung.ilike(like),
                User.email.ilike(like)
            )
        )

    users = (
        query
        .order_by(User.ngay_tao.desc())
        .all()
    )

    return [serialize_user(user) for user in users]


@router.put("/{ma_nguoi_dung}/doi-quyen")
def change_role(
    ma_nguoi_dung: UUID,
    quyen: str = Query(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    if quyen not in ["user", "admin"]:
        raise HTTPException(
            status_code=400,
            detail="Quyền không hợp lệ"
        )

    user = (
        db.query(User)
        .filter(User.ma_nguoi_dung == ma_nguoi_dung)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản"
        )

    user.quyen = quyen

    db.commit()
    db.refresh(user)

    return serialize_user(user)


@router.put("/{ma_nguoi_dung}/khoa")
def toggle_lock_user(
    ma_nguoi_dung: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    if ma_nguoi_dung == current_user.ma_nguoi_dung:
        raise HTTPException(
            status_code=400,
            detail="Không thể khóa chính tài khoản của bạn"
        )

    user = (
        db.query(User)
        .filter(User.ma_nguoi_dung == ma_nguoi_dung)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản"
        )

    user.trang_thai = not bool(user.trang_thai)

    db.commit()
    db.refresh(user)

    return serialize_user(user)


@router.delete("/{ma_nguoi_dung}")
def delete_user(
    ma_nguoi_dung: UUID,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    if ma_nguoi_dung == current_user.ma_nguoi_dung:
        raise HTTPException(
            status_code=400,
            detail="Không thể xóa chính tài khoản của bạn"
        )

    user = (
        db.query(User)
        .filter(User.ma_nguoi_dung == ma_nguoi_dung)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Không tìm thấy tài khoản"
        )

    db.delete(user)
    db.commit()

    return {
        "message": "Xóa tài khoản thành công"
    }