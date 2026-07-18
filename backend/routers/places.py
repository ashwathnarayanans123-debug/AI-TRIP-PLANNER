"""OpenStreetMap places routes (Nominatim + Overpass)."""

from typing import Optional

from fastapi import APIRouter, Query

from schemas import PlacesResponse
from services.places_service import fetch_places

router = APIRouter(tags=["places"])


@router.get("/places", response_model=PlacesResponse)
async def get_places(
    destination: str = Query(..., min_length=2),
    type: Optional[str] = Query(
        default=None,
        description="Optional filter: hotel | restaurant | tourist_attraction",
    ),
) -> PlacesResponse:
    """
    Return hotels, restaurants, and attractions near a destination.
    Uses free Nominatim geocoding + Overpass POI search (no API key).
    """
    return await fetch_places(destination, place_type=type)
