class PlaceRankingService:

    @staticmethod
    def normalize_rating(rating):
        if not rating:
            return 0

        return min(float(rating) / 5, 1)

    @staticmethod
    def normalize_reviews(so_danh_gia):
        if not so_danh_gia:
            return 0

        return min(int(so_danh_gia) / 1000, 1)

    @staticmethod
    def rank_places(places):
        ranked_places = []

        for place in places:
            metadata = place["metadata"]

            semantic_score = place.get(
                "semantic_score",
                0
            )

            rating_score = (
                PlaceRankingService
                .normalize_rating(
                    metadata.get("danh_gia", 0)
                )
            )

            review_score = (
                PlaceRankingService
                .normalize_reviews(
                    metadata.get("so_danh_gia", 0)
                )
            )

            final_score = (
                semantic_score * 0.75
                + rating_score * 0.15
                + review_score * 0.10
            )

            place["ranking"] = {
                "semantic_score": round(semantic_score, 4),
                "rating_score": round(rating_score, 4),
                "review_score": round(review_score, 4),
                "final_score": round(final_score, 4)
            }

            ranked_places.append(place)

        return sorted(
            ranked_places,
            key=lambda x: x["ranking"]["final_score"],
            reverse=True
        )