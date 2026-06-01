import random
from fastapi import APIRouter, Query

router = APIRouter(
    prefix="/place-rating",
    tags=["Place Rating"]
)


@router.get("")
def get_place_rating(
    lat: float = Query(...),
    lng: float = Query(...)
):
    return {
        "danh_gia": round(random.uniform(4.0, 5.0), 1),
        "so_danh_gia": random.randint(100, 200)
    }