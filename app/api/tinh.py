from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.tinh import Tinh

router = APIRouter(prefix="/tinh", tags=["Tinh"])

@router.get("/tinh")
def get_tinh(db: Session = Depends(get_db)):
    return db.query(Tinh).all()