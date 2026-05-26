from fastapi import FastAPI
from app.api import auth, user, dia_diem_admin
from app.api import dia_diem, yeu_thich, tinh, loai_dia_diem, chi_phi, ai
from app.api import chuyen_di
from app.api import trip_options
from app.api import the
from fastapi.middleware.cors import CORSMiddleware
from app.api.ai_planner_api import (router as ai_planner_router)
from app.api import loai_du_lich

app = FastAPI()

app.include_router(auth.router)
app.include_router(user.router)
app.include_router(dia_diem.router)
app.include_router(yeu_thich.router)
app.include_router(dia_diem_admin.router)
app.include_router(tinh.router)
app.include_router(loai_dia_diem.router)
app.include_router(ai.router)
app.include_router(chi_phi.router)
app.include_router(the.router)
app.include_router(ai_planner_router)
app.include_router(loai_du_lich.router)
app.include_router(trip_options.router)
app.include_router(chuyen_di.router)
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