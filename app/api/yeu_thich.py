from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import yeu_thich_service
from app.core.deps import get_current_user

router = APIRouter(prefix="/yeu-thich", tags=["YeuThich"])

@router.post("/{id}/toggle")
def toggle(
    id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return yeu_thich_service.toggle_favorite(db, current_user, id)


@router.get("/me")
def get_my(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return yeu_thich_service.get_my_favorites(db, current_user)