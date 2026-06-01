from fastapi import APIRouter, Query, HTTPException

from app.services.geocoding_service import GeocodingService


router = APIRouter(
    prefix="/geo",
    tags=["Geocoding"]
)


@router.get("/search")
def search_location(
    query: str = Query(...)
):
    try:
        return GeocodingService.search_location(
            query
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )