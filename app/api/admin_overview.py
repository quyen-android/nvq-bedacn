from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import extract, func

from app.db.session import get_db
from app.core.deps import get_current_user
from app.models.chuyen_di import ChuyenDi
from app.models.user import User


router = APIRouter(
    prefix="/admin/overview",
    tags=["Admin Overview"]
)


def check_admin(current_user):
    if current_user.quyen != "admin":
        raise HTTPException(
            status_code=403,
            detail="Bạn không có quyền truy cập"
        )


@router.get("")
def get_admin_overview(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    check_admin(current_user)

    current_year = date.today().year

    total_trips = db.query(ChuyenDi).count()

    completed_trips = (
        db.query(ChuyenDi)
        .filter(ChuyenDi.trang_thai == "hoan_thanh")
        .count()
    )

    draft_trips = (
        db.query(ChuyenDi)
        .filter(ChuyenDi.trang_thai == "ban_nhap")
        .count()
    )

    created_stats = (
        db.query(
            extract("month", ChuyenDi.ngay_tao).label("month"),
            func.count(ChuyenDi.ma_chuyen_di).label("total")
        )
        .filter(
            extract("year", ChuyenDi.ngay_tao) == current_year
        )
        .group_by("month")
        .all()
    )

    travel_stats = (
        db.query(
            extract("month", ChuyenDi.ngay_di).label("month"),
            func.count(ChuyenDi.ma_chuyen_di).label("total")
        )
        .filter(
            extract("year", ChuyenDi.ngay_di) == current_year
        )
        .group_by("month")
        .all()
    )

    created_map = {
        int(item.month): int(item.total)
        for item in created_stats
    }

    travel_map = {
        int(item.month): int(item.total)
        for item in travel_stats
    }

    monthly_stats = []

    for month in range(1, 13):
        monthly_stats.append({
            "month": month,
            "label": f"Tháng {month}",
            "created_count": created_map.get(month, 0),
            "travel_count": travel_map.get(month, 0)
        })

    total_users = db.query(User).count()

    return {
        "total_users": total_users,
        "total_trips": total_trips,
        "completed_trips": completed_trips,
        "draft_trips": draft_trips,
        "year": current_year,
        "monthly_stats": monthly_stats
    }