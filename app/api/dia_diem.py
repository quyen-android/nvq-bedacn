from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.dia_diem_service import DiaDiemService
from app.core.deps import get_current_user_optional
from app.models.user import User

router = APIRouter(prefix="/dia-diem", tags=["DiaDiem"])


@router.get("")
def get_dia_diem(
    loai: str = None,
    search: str = None,
    the: str = None,
    min_gia: float=None,
    max_gia: float=None,
    danh_gia: float = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_optional),
):
    tags = the.split(",") if the else None

    return DiaDiemService.get_dia_diem_list(
        db,
        loai=loai,
        search=search,
        tags=tags,
        min_gia=min_gia,
        max_gia=max_gia,
        danh_gia=danh_gia,
        current_user=current_user
    )