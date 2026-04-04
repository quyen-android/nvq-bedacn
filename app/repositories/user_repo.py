from sqlalchemy.orm import Session
from app.models.user import User

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session,ten_nguoi_dung:str, email: str, mat_khau: str):
    user = User(ten_nguoi_dung = ten_nguoi_dung, email=email, mat_khau = mat_khau)
    db.add(user)
    print("Before commit")
    db.commit()
    print("After commit")
    db.refresh(user)
    return user