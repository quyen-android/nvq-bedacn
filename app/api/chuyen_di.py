from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.chuyen_di import ChuyenDiCreate
from app.services.trip_service import TripService
from app.core.deps import get_current_user


router = APIRouter(
    prefix="/chuyen-di",
    tags=["Chuyến đi"]
)


@router.post("")
def create_chuyen_di(
    data: ChuyenDiCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    try:
        chuyen_di = TripService.create_chuyen_di(
            db=db,
            data=data,
            current_user=current_user
        )

        return {
            "message": "Tạo chuyến đi thành công",
            "ma_chuyen_di": chuyen_di.ma_chuyen_di,
            "ten_chuyen_di": chuyen_di.ten_chuyen_di
        }

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )