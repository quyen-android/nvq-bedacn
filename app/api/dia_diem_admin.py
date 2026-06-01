from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.deps import require_role
from app.services.dia_diem_service import DiaDiemService

router = APIRouter(
    prefix="/dia-diem-admin",
    tags=["DiaDiemAdmin"]
)

service = DiaDiemService()


@router.post("")
async def create(
    ten: str = Form(...),
    ma_tinh: str = Form(...),
    ma_loai: str = Form(...),
    dia_chi: str = Form(None),
    mo_ta: str = Form(None),
    kinh_do: float = Form(None),
    vi_do: float = Form(None),
    gia_trung_binh: float = Form(None),
    danh_gia: float = Form(None),
    so_danh_gia: int = Form(None),
    gio_mo: str = Form(None),
    gio_dong: str = Form(None),
    website: str = Form(None),
    sdt: str = Form(None),

    anh_chinh: UploadFile = File(...),
    anh_phu: list[UploadFile] = File(...),

    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return await service.create(
        db=db,
        ten=ten,
        ma_tinh=ma_tinh,
        ma_loai=ma_loai,
        dia_chi=dia_chi,
        mo_ta=mo_ta,
        kinh_do=kinh_do,
        vi_do=vi_do,
        gia_trung_binh=gia_trung_binh,
        danh_gia=danh_gia,
        so_danh_gia=so_danh_gia,
        gio_mo=gio_mo,
        gio_dong=gio_dong,
        website=website,
        sdt=sdt,
        anh_chinh=anh_chinh,
        anh_phu=anh_phu
    )


@router.put("/{id}")
async def update_dia_diem(
    id: str,

    ten: str = Form(None),
    dia_chi: str = Form(None),
    mo_ta: str = Form(None),

    kinh_do: float = Form(None),
    vi_do: float = Form(None),

    ma_tinh: str = Form(None),
    ma_loai: str = Form(None),

    gia_trung_binh: float = Form(None),
    danh_gia: float = Form(None),
    so_danh_gia: int = Form(None),

    gio_mo: str = Form(None),
    gio_dong: str = Form(None),

    website: str = Form(None),
    sdt: str = Form(None),

    anh_chinh: UploadFile = File(None),

    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return await service.update(
        db=db,
        dia_diem_id=id,
        ten=ten,
        dia_chi=dia_chi,
        mo_ta=mo_ta,
        kinh_do=kinh_do,
        vi_do=vi_do,
        ma_tinh=ma_tinh,
        ma_loai=ma_loai,
        gia_trung_binh=gia_trung_binh,
        danh_gia=danh_gia,
        so_danh_gia=so_danh_gia,
        gio_mo=gio_mo,
        gio_dong=gio_dong,
        website=website,
        sdt=sdt,
        anh_chinh=anh_chinh
    )


@router.post("/{id}/sub-images")
async def add_sub_images(
    id: str,
    anh_phu: list[UploadFile] = File(...),
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return await service.add_sub_images(
        db=db,
        dia_diem_id=id,
        anh_phu=anh_phu
    )


@router.delete("/images/{ma_anh}")
def delete_sub_image(
    ma_anh: str,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return service.delete_sub_image(
        db=db,
        ma_anh=ma_anh
    )


@router.get("")
def get_all(
    db: Session = Depends(get_db)
):
    return service.get_all(db)


@router.get("/{id}")
def get_one(
    id: str,
    db: Session = Depends(get_db)
):
    return service.get_by_id(db, id)


@router.delete("/{id}")
def delete(
    id: str,
    current_user=Depends(require_role("admin")),
    db: Session = Depends(get_db)
):
    return service.delete(db, id)