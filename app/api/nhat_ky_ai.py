from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import get_current_user
from app.services.nhat_ky_ai_service import NhatKyAIService


router = APIRouter(
    prefix="/nhat-ky-ai",
    tags=["Nhật ký AI"]
)


@router.get("")
def get_my_ai_logs(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    logs = NhatKyAIService.get_my_logs(
        db=db,
        current_user=current_user
    )

    return [
        {
            "ma_log": str(item.ma_log),
            "ma_nguoi_dung": (
                str(item.ma_nguoi_dung)
                if item.ma_nguoi_dung else None
            ),
            "ma_chuyen_di": (
                str(item.ma_chuyen_di)
                if item.ma_chuyen_di else None
            ),
            "cau_hoi": item.cau_hoi,
            "cau_tra_loi": item.cau_tra_loi,
            "ngu_canh": item.ngu_canh,
            "model": item.model,
            "tokens_su_dung": item.tokens_su_dung,
            "tg_phan_hoi": item.tg_phan_hoi,
            "danh_gia": item.danh_gia,
            "ngay_tao": item.ngay_tao
        }
        for item in logs
    ]


@router.put("/{ma_log}/danh-gia")
def danh_gia_ai_log(
    ma_log: UUID,
    danh_gia: int = Query(..., ge=1, le=5),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        log = NhatKyAIService.danh_gia_log(
            db=db,
            ma_log=ma_log,
            danh_gia=danh_gia,
            current_user=current_user
        )

        return {
            "message": "Đánh giá thành công",
            "ma_log": str(log.ma_log),
            "danh_gia": log.danh_gia
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )