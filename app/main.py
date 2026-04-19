from fastapi import FastAPI
from app.api import auth, user
from app.api import dia_diem, yeu_thich

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dia_diem.router)
app.include_router(yeu_thich.router)