from app.db.session import SessionLocal
from app.repositories import dia_diem_repo
from app.services.rag_service import RagService

db = SessionLocal()

# xóa collection cũ
RagService.client.delete_collection(
    "dia_diem"
)

RagService.collection = (
    RagService.client.get_or_create_collection(
        name="dia_diem"
    )
)

places = dia_diem_repo.get_all(db)

for place in places:

    try:
        RagService.add_place(place)

        print(
            f"OK: {place.ten}"
        )

    except Exception as e:

        print(
            f"Lỗi {place.ten}: {e}"
        )