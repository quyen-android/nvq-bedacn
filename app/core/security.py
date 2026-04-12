from passlib.context import CryptContext
from app.core.config import settings
from datetime import datetime, timedelta
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str):
    return pwd_context.hash(password)    

def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)
