import chromadb
from sentence_transformers import SentenceTransformer
from sqlalchemy import text
import json
from app.core.config import settings
from app.models import DiaDiem


class RagService:
    model = SentenceTransformer(
        "paraphrase-multilingual-MiniLM-L12-v2"
    )

    client = chromadb.PersistentClient(
        path="./chroma_db"
    )

    collection = client.get_or_create_collection(
        name="dia_diem"
    )

    @classmethod
    def get_golden_hours(cls, db, ma_dia_diem):
        query = text("""
            SELECT 
                gio_bat_dau,
                gio_ket_thuc,
                thang_bat_dau,
                thang_ket_thuc
            FROM khung_gio_vang
            WHERE ma_dia_diem = :ma_dia_diem
        """)

        rows = db.execute(
            query,
            {"ma_dia_diem": ma_dia_diem}
        ).fetchall()

        return [
            {
                "start": row.gio_bat_dau.strftime("%H:%M"),
                "end": row.gio_ket_thuc.strftime("%H:%M"),
                "month_start": row.thang_bat_dau,
                "month_end": row.thang_ket_thuc
            }
            for row in rows
        ]

    @classmethod
    def build_document(cls, dia_diem: DiaDiem, db=None):
        tags_text = ", ".join([
            item.the.ten_the
            for item in dia_diem.the_dia_diems
            if item.the
        ])

        golden_text = ""

        if db:
            golden_hours = cls.get_golden_hours(
                db,
                dia_diem.ma_dia_diem
            )

            if golden_hours:
                golden_lines = []

                for item in golden_hours:
                    golden_lines.append(
                        f"Khung giờ vàng: {item['start']} - {item['end']}, "
                        f"áp dụng tháng {item['month_start']} đến tháng {item['month_end']}"
                    )

                golden_text = "\n".join(golden_lines)

        return f"""
            Tên địa điểm: {dia_diem.ten or ""}
            Loại địa điểm: {dia_diem.loai.ten_loai if dia_diem.loai else ""}
            Tags: {tags_text}
            Mô tả: {dia_diem.mo_ta or ""}
            Địa chỉ: {dia_diem.dia_chi or ""}
            Giá trung bình: {dia_diem.gia_trung_binh or 0}
            Đánh giá: {dia_diem.danh_gia or 0}
            Số đánh giá: {dia_diem.so_danh_gia or 0}
            Giờ mở: {dia_diem.gio_mo or ""}
            Giờ đóng: {dia_diem.gio_dong or ""}
            Tỉnh: {dia_diem.tinh.ten_tinh if dia_diem.tinh else ""}
            {golden_text}
            """

    @classmethod
    def build_metadata(cls, dia_diem: DiaDiem, db=None):
        golden_hours = []

        if db:
            golden_hours = cls.get_golden_hours(
                db,
                dia_diem.ma_dia_diem
            )

        return {
            "ma_dia_diem": str(dia_diem.ma_dia_diem),
            "ten": dia_diem.ten,
            "dia_chi": dia_diem.dia_chi,
            "loai": dia_diem.loai.ten_loai if dia_diem.loai else "",
            "tinh": dia_diem.tinh.ten_tinh if dia_diem.tinh else "",
            "gia": float(dia_diem.gia_trung_binh or 0),
            "danh_gia": float(dia_diem.danh_gia or 0),
            "so_danh_gia": int(dia_diem.so_danh_gia or 0),
            "lat": float(dia_diem.vi_do or 0),
            "lon": float(dia_diem.kinh_do or 0),
            "gio_mo": str(dia_diem.gio_mo) if dia_diem.gio_mo else "",
            "gio_dong": str(dia_diem.gio_dong) if dia_diem.gio_dong else "",
            "golden_hours": json.dumps(golden_hours, ensure_ascii=False)
        }

    @classmethod
    def upsert_place(cls, dia_diem: DiaDiem, db=None):
        document = cls.build_document(
            dia_diem,
            db=db
        )

        embedding = cls.model.encode(
            document
        ).tolist()

        cls.collection.upsert(
            ids=[str(dia_diem.ma_dia_diem)],
            documents=[document],
            embeddings=[embedding],
            metadatas=[
                cls.build_metadata(
                    dia_diem,
                    db=db
                )
            ]
        )

    @classmethod
    def add_place(cls, dia_diem: DiaDiem, db=None):
        cls.upsert_place(dia_diem, db=db)

    @classmethod
    def update_place(cls, dia_diem: DiaDiem, db=None):
        cls.upsert_place(dia_diem, db=db)

    @classmethod
    def delete_place(cls, dia_diem_id):
        cls.collection.delete(
            ids=[str(dia_diem_id)]
        )

    @staticmethod
    def build_where_filter(loai=None, tinh=None):
        conditions = []

        if loai:
            conditions.append({"loai": loai})

        if tinh:
            conditions.append({"tinh": tinh})

        if not conditions:
            return None

        if len(conditions) == 1:
            return conditions[0]

        return {"$and": conditions}

    @staticmethod
    def calculate_semantic_score(distance):
        try:
            distance = float(distance)
            return 1 / (1 + distance)
        except:
            return 0

    @classmethod
    def get_top_k(cls, so_ngay):
        return min(
            max(
                so_ngay * 10,20
            ),
            60
        )

    @classmethod
    def search_places(
        cls,
        query,
        loai=None,
        tinh=None,
        so_ngay=1,
        top_k=None
    ):
        if not top_k:
            top_k = cls.get_top_k(so_ngay)

        query_embedding = cls.model.encode(
            query
        ).tolist()

        where = cls.build_where_filter(
            loai=loai,
            tinh=tinh
        )

        results = cls.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where
        )

        if (
            not results
            or not results.get("documents")
            or not results["documents"][0]
        ):
            return []

        places = []

        for index, document in enumerate(results["documents"][0]):
            metadata = results["metadatas"][0][index]
            distance = float(results["distances"][0][index])

            places.append({
                "ma_dia_diem": metadata.get("ma_dia_diem"),
                "document": document,
                "metadata": metadata,
                "distance": round(distance, 4),
                "semantic_score": round(
                    cls.calculate_semantic_score(distance),
                    4
                )
            })

        return sorted(
            places,
            key=lambda x: x["semantic_score"],
            reverse=True
        )