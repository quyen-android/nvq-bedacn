from fastapi import FastAPI
from app.api import auth, user, dia_diem_admin
from app.api import dia_diem, yeu_thich, tinh, loai_dia_diem

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dia_diem.router)
app.include_router(yeu_thich.router)
app.include_router(dia_diem_admin.router)
app.include_router(tinh.router)
app.include_router(loai_dia_diem.router)