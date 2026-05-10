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
    def build_document(cls, dia_diem):

        return f"""
        Tên: {dia_diem.ten}

        Mô tả:
        {dia_diem.mo_ta}

        Địa chỉ:
        {dia_diem.dia_chi}

        Giá:
        {dia_diem.gia_trung_binh}

        """

    @classmethod
    def add_place(cls, dia_diem):

        document = cls.build_document(dia_diem)

        embedding = cls.model.encode(
            document
        ).tolist()

        cls.collection.add(
            ids=[str(dia_diem.ma_dia_diem)],
            documents=[document],
            embeddings=[embedding]
        )

    @classmethod
    def update_place(cls, dia_diem):

        document = cls.build_document(dia_diem)

        embedding = cls.model.encode(
            document
        ).tolist()

        cls.collection.update(
            ids=[str(dia_diem.ma_dia_diem)],
            documents=[document],
            embeddings=[embedding]
        )

    @classmethod
    def delete_place(cls, dia_diem_id):

        cls.collection.delete(
            ids=[str(dia_diem_id)]
        )

    @classmethod
    def search_places(cls, query):

        query_embedding = cls.model.encode(
            query
        ).tolist()

        return cls.collection.query(
            query_embeddings=[query_embedding],
            n_results=5
        )