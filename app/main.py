from fastapi import FastAPI
from app.api.auth import router as auth_router
from app.db.base import Base
from app.db.session import engine
from app.models.user import User

app = FastAPI()

app.include_router(auth_router)