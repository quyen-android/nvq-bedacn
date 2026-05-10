from pydantic import BaseModel
from typing import List
from datetime import date


class GenerateItineraryRequest(BaseModel):
    ma_nguoi_dung: str
    ma_tinh_di: str
    ma_tinh_den: str

    ten_chuyen_di: str

    ngay_di: date
    ngay_ve: date

    so_nguoi: int
    ngan_sach: float

    loai_du_lich: List[str] = []
    yeu_cau_dac_biet: List[str] = []
    so_thich_am_thuc: List[str] = []