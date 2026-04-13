from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository
from app.core.security import verify_password, hash_password


class PasswordService:

    def __init__(self):
        self.user_repo = UserRepository()
        self.token_repo = TokenRepository()

    def change_password(self, db: Session, user_id: str, current_password: str, new_password: str, confirm_password: str):

        user = self.user_repo.get_user_by_id(db, user_id)

        if not user:
            raise HTTPException(404, "User không tồn tại")

        if not verify_password(current_password, user.mat_khau):
            raise HTTPException(400, "Sai mật khẩu")

        if new_password != confirm_password:
            raise HTTPException(400, "Không trùng mật khẩu")

        user.mat_khau = hash_password(new_password)

        self.token_repo.revoke_all_by_user(db, user_id)

        db.commit()

        return {"message": "Đổi mật khẩu thành công"}