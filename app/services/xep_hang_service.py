class XepHangService:

    @staticmethod
    def normalize_rating(rating):
        if rating is None:
            return 0

        try:
            return min(
                max(float(rating) / 50, 0),
                1
            )
        except Exception:
            return 0

    @staticmethod
    def normalize_reviews(so_danh_gia):
        if so_danh_gia is None:
            return 0

        try:
            return min(
                max(int(so_danh_gia) / 10000, 0),
                1
            )
        except Exception:
            return 0

    @classmethod
    def calculate_final_score(
        cls,
        semantic_score,
        rating_score,
        review_score
    ):
        return (
            semantic_score 
            + rating_score * 0.15
            + review_score * 0.1
        )

    @classmethod
    def rank_place(cls, place):
        metadata = place.get("metadata", {})

        try:
            semantic_score = float(
                place.get("semantic_score", 0)
            )
        except Exception:
            semantic_score = 0

        semantic_score = min(
            max(semantic_score, 0),
            1
        )

        rating_score = cls.normalize_rating(
            metadata.get("danh_gia", 0)
        )

        review_score = cls.normalize_reviews(
            metadata.get("so_danh_gia", 0)
        )

        final_score = cls.calculate_final_score(
            semantic_score=semantic_score,
            rating_score=rating_score,
            review_score=review_score
        )

        return {
            **place,
            "ranking": {
                "semantic_score": round(semantic_score, 4),
                "rating_score": round(rating_score, 4),
                "review_score": round(review_score, 4),
                "final_score": round(final_score, 4)
            }
        }

    @classmethod
    def rank_places(cls, places):
        if not places:
            return []

        ranked_places = [
            cls.rank_place(place)
            for place in places
        ]

        return sorted(
            ranked_places,
            key=lambda x: x["ranking"]["final_score"],
            reverse=True
        )

    @classmethod
    def get_top_places(cls, places, limit=30):
        ranked_places = cls.rank_places(places)

        return ranked_places[:limit]