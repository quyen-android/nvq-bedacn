from typing import Optional
from fastapi import Form

class UserUpdate:
    def __init__(
        self,
        ten_nguoi_dung: Optional[str] = Form(None),
        sdt: Optional[str] = Form(None),
        dia_chi: Optional[str] = Form(None),
    ):
        self.ten_nguoi_dung = ten_nguoi_dung
        self.sdt = sdt
        self.dia_chi = dia_chi