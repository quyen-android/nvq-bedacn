import chromadb

from sentence_transformers import SentenceTransformer


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
    def build_document(
        cls,
        dia_diem
    ):

        tags_text = ", ".join([

            item.the.ten_the

            for item in dia_diem.the_dia_diems

            if item.the
        ])

        return f"""
        Tên địa điểm:
        {dia_diem.ten}

        Loại địa điểm:
        {dia_diem.loai.ten_loai if dia_diem.loai else ""}

        Tags:
        {tags_text}

        Mô tả:
        {dia_diem.mo_ta}

        Địa chỉ:
        {dia_diem.dia_chi}

        Giá trung bình:
        {dia_diem.gia_trung_binh}

        Đánh giá:
        {dia_diem.danh_gia}

        Giờ mở:
        {dia_diem.gio_mo}

        Giờ đóng:
        {dia_diem.gio_dong}
        """

    @classmethod
    def build_metadata(
        cls,
        dia_diem
    ):
        return {
            "ma_dia_diem": str(
                dia_diem.ma_dia_diem
            ),

            "ten": (
                dia_diem.ten
                or ""
            ),

            "loai": (
                dia_diem.loai.ten_loai
                if dia_diem.loai
                else ""
            ),

            "gia": float(
                dia_diem.gia_trung_binh
                or 0
            ),

            "danh_gia": float(
                dia_diem.danh_gia
                or 0
            ),

            "so_danh_gia": int(
                dia_diem.so_danh_gia
                or 0
            ),

            "lat": float(
                dia_diem.vi_do
                or 0
            ),

            "lon": float(
                dia_diem.kinh_do
                or 0
            ),

            "tinh": (
                dia_diem.tinh.ten_tinh
                if dia_diem.tinh
                else ""
            ),

            "gio_mo": (
                str(dia_diem.gio_mo)
                if dia_diem.gio_mo
                else None
            ),

            "gio_dong": (
                str(dia_diem.gio_dong)
                if dia_diem.gio_dong
                else None
            ),
        }

    @classmethod
    def add_place(
        cls,
        dia_diem
    ):

        document = cls.build_document(
            dia_diem
        )

        embedding = cls.model.encode(
            document
        ).tolist()

        cls.collection.add(
            ids=[
                str(dia_diem.ma_dia_diem)
            ],

            documents=[
                document
            ],

            embeddings=[
                embedding
            ],

            metadatas=[
                cls.build_metadata(
                    dia_diem
                )
            ]
        )

    @classmethod
    def update_place(
        cls,
        dia_diem
    ):

        document = cls.build_document(
            dia_diem
        )

        embedding = cls.model.encode(
            document
        ).tolist()

        cls.collection.update(
            ids=[
                str(dia_diem.ma_dia_diem)
            ],

            documents=[
                document
            ],

            embeddings=[
                embedding
            ],

            metadatas=[
                cls.build_metadata(
                    dia_diem
                )
            ]
        )

    @classmethod
    def delete_place(
        cls,
        dia_diem_id
    ):

        cls.collection.delete(
            ids=[
                str(dia_diem_id)
            ]
        )

    @classmethod
    def search_places(
        cls,
        query,
        loai=None,
        so_ngay=1
    ):

        n_results = max(
            so_ngay * 4,
            30
        )

        query_embedding = cls.model.encode(
            query
        ).tolist()

        where = None

        if loai:
            where = {
                "loai": loai
            }

        results = cls.collection.query(
            query_embeddings=[
                query_embedding
            ],
            n_results=n_results,
            where=where
        )

        places = []

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]

        for i in range(
            len(documents)
        ):

            distance = distances[i]

            semantic_score = 1 / (
                distance + 0.1
            )

            places.append({
                "document": documents[i],
                "metadata": metadatas[i],
                "distance": distance,
                "semantic_score": semantic_score
            })

        return places