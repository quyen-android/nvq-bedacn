import re
from fastapi import HTTPException


def validate_required(value: str, field_name: str):
    if not value or value.strip() == "":
        raise HTTPException(
            status_code=400,
            detail=f"{field_name} không được để trống"
        )


def validate_email(email: str):

    validate_required(email, "Email")

    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'

    if not re.match(pattern, email):
        raise HTTPException(
            status_code=400,
            detail="Email không hợp lệ"
        )


def validate_phone(sdt: str):

    validate_required(sdt, "Số điện thoại")

    pattern = r'^0[0-9]{9}$'

    if not re.match(pattern, sdt):
        raise HTTPException(
            status_code=400,
            detail="Số điện thoại không hợp lệ"
        )


def validate_password(password: str):

    validate_required(password, "Mật khẩu")

    pattern = (
        r'^(?=.*[a-z])'
        r'(?=.*[A-Z])'
        r'(?=.*\d)'
        r'(?=.*[@$!%*?&])'
        r'[A-Za-z\d@$!%*?&]{8,}$'
    )

    if not re.match(pattern, password):
        raise HTTPException(
            status_code=400,
            detail=(
                "Mật khẩu phải có ít nhất 8 ký tự, "
                "gồm chữ hoa, chữ thường, số "
                "và ký tự đặc biệt"
            )
        )