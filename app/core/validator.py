import re
from fastapi import HTTPException

def validate_email(email: str):
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    if not re.match(pattern, email):
        raise HTTPException(400, "Email không hợp lệ")

def validate_phone(sdt: str):
    pattern = r'^0[0-9]{9}$'
    if not re.match(pattern, sdt):
        raise HTTPException(400, "Số điện thoại không hợp lệ")