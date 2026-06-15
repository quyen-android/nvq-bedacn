from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, user, dia_diem_admin
from app.api import dia_diem, yeu_thich, tinh, loai_dia_diem
from app.api import chuyen_di
from app.api import lua_chon_chuyen_di
from app.api import the
from app.api.ai_planner_api import (router as ai_planner_router)
from app.api import loai_du_lich
from app.api import so_thich_am_thuc
from app.api import yeu_cau_dac_biet
from app.api import tinh
from app.api import geocoding
from app.api import khung_gio_vang
from app.api import place_rating
from app.api import lich_trinh
from app.api import phuong_tien
from app.api import thong_ke_chi_phi
from app.api import chatbot
from app.api import nhat_ky_ai
from app.api import thoi_tiet
from app.api import admin_overview
from app.api import admin_tai_khoan



app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)

app.include_router(dia_diem.router)
app.include_router(yeu_thich.router)
app.include_router(lich_trinh.router)
app.include_router(phuong_tien.router)
app.include_router(thong_ke_chi_phi.router)
app.include_router(chatbot.router)
app.include_router(nhat_ky_ai.router)

app.include_router(dia_diem_admin.router)
app.include_router(admin_overview.router)
app.include_router(tinh.router)
app.include_router(loai_dia_diem.router)
app.include_router(the.router)
app.include_router(ai_planner_router)
app.include_router(loai_du_lich.router)
app.include_router(lua_chon_chuyen_di.router)
app.include_router(chuyen_di.router)
app.include_router(so_thich_am_thuc.router)
app.include_router(yeu_cau_dac_biet.router)
app.include_router(tinh.router)
app.include_router(khung_gio_vang.router)
app.include_router(admin_tai_khoan.router)

app.include_router(thoi_tiet.router)
app.include_router(geocoding.router)
app.include_router(place_rating.router)
print("MAIN.PY ĐANG CHẠY")
print(place_rating.router.routes)

app.mount(
    "/uploads",
    StaticFiles(directory="uploads"),
    name="uploads"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)