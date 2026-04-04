from sqlalchemy.orm import Session
from app.repositories.user_repo import get_user_by_email, create_user
from app.core.security import hash_password

def register_user(db: Session,ten_nguoi_dung:str, email: str, mat_khau: str):
    
    # 1. check email tồn tại
    existing_user = get_user_by_email(db, email)
    if existing_user:
        raise ValueError("Email already exists")

    # 2. hash password
    hashed_password = hash_password(mat_khau)

    # 3. tạo user
    user = create_user(db,ten_nguoi_dung, email, hashed_password)

    return user