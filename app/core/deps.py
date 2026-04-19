from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.db.session import get_db
from app.core.config import settings
from app.repositories.user_repo import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
security = HTTPBearer(auto_error=False)

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token không hợp lệ"
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token không hợp lệ hoặc hết hạn"
        )

    user_repo = UserRepository()

    user = user_repo.get_user_by_id(db, str(user_id))

    if not user:
        raise HTTPException(
            status_code=401,
            detail="User không tồn tại"
        )

    if not user.trang_thai:
        raise HTTPException(
            status_code=403,
            detail="Tài khoản bị khóa"
        )

    return user

def get_current_user_optional(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials = Depends(security)
):
    if not credentials:
        return None

    try:
        token = credentials.credentials

        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id: str = payload.get("sub")
        token_type: str = payload.get("type")

        if user_id is None or token_type != "access":
            return None

    except JWTError:
        return None

    user_repo = UserRepository()
    user = user_repo.get_user_by_id(db, str(user_id))

    if not user or not user.trang_thai:
        return None

    return user 

def require_role(role: str):
    def checker(current_user = Depends(get_current_user)):
        if current_user.quyen != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Không có quyền truy cập"
            )
        return current_user
    return checker