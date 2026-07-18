"""Weather API routes."""

from fastapi import APIRouter, Query

from schemas import WeatherResponse
from services.weather_service import fetch_weather

router = APIRouter(tags=["weather"])


@router.get("/weather", response_model=WeatherResponse)
async def get_weather(
    city: str = Query(..., min_length=2, description="City or destination name"),
) -> WeatherResponse:
    """Return current weather and a 5-day forecast for the given city."""
    return await fetch_weather(city)
