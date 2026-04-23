from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.loai_dia_diem import LoaiDiaDiem

router = APIRouter(prefix="/loai_dia_diem", tags=["LoaiDiaDiem"])

@router.get("/loai_dia_diem")
def get_loai_dia_diem(db: Session = Depends(get_db)):
    return db.query(LoaiDiaDiem).all()