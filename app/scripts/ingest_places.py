# app/scripts/ingest_places.py
from app.models import *
from app.db.session import SessionLocal
from app.models.dia_diem import DiaDiem
from app.services.rag_service import RagService


def ingest_places():

    print("🚀 Bắt đầu ingest...")

    db = SessionLocal()

    try:

        places = db.query(DiaDiem).all()

        print(f"Tìm thấy {len(places)} địa điểm")

        for place in places:

            try:

                RagService.add_place(place)

                print(f"✅ Đã ingest: {place.ten}")

            except Exception as e:

                print(f"❌ Lỗi {place.ten}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    ingest_places()