from sqlalchemy.orm import Session
from app.models.user import User

class UserRepository:
    def get_user_by_email(self, db, email):
        return db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, db, user_id):
        return db.query(User).filter(User.ma_nguoi_dung == user_id).first()
    
    def create_user(self, db: Session,ten_nguoi_dung:str, email: str, mat_khau: str):
        user = User(ten_nguoi_dung = ten_nguoi_dung, email=email, mat_khau = mat_khau)
        db.add(user)
        db.commit()
        db.refresh(user)
        return user