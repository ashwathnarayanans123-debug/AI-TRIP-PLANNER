"""
Weather integration with free-first providers.

Priority:
  1. OpenWeather (if key is valid)
  2. Open-Meteo + Nominatim geocoding (no key, always free)
  3. Deterministic demo fallback
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Optional

import httpx

from schemas import WeatherDay, WeatherResponse
from utils.helpers import get_env

logger = logging.getLogger(__name__)

OPENWEATHER_BASE = "https://api.openweathermap.org/data/2.5"
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"

HTTP_HEADERS = {
    "User-Agent": "WanderAI-TripPlanner/1.0 (educational; contact=hello@wanderai.app)",
    "Accept": "application/json",
}

# WMO weather codes → (label, description, icon-ish code)
WMO_CODES: dict[int, tuple[str, str, str]] = {
    0: ("Clear", "clear sky", "01d"),
    1: ("Clear", "mainly clear", "01d"),
    2: ("Clouds", "partly cloudy", "02d"),
    3: ("Clouds", "overcast", "03d"),
    45: ("Fog", "foggy", "50d"),
    48: ("Fog", "depositing rime fog", "50d"),
    51: ("Drizzle", "light drizzle", "09d"),
    53: ("Drizzle", "moderate drizzle", "09d"),
    55: ("Drizzle", "dense drizzle", "09d"),
    61: ("Rain", "slight rain", "10d"),
    63: ("Rain", "moderate rain", "10d"),
    65: ("Rain", "heavy rain", "10d"),
    71: ("Snow", "slight snow", "13d"),
    73: ("Snow", "moderate snow", "13d"),
    75: ("Snow", "heavy snow", "13d"),
    80: ("Rain", "rain showers", "09d"),
    81: ("Rain", "heavy rain showers", "09d"),
    82: ("Rain", "violent rain showers", "09d"),
    95: ("Thunderstorm", "thunderstorm", "11d"),
    96: ("Thunderstorm", "thunderstorm with hail", "11d"),
    99: ("Thunderstorm", "thunderstorm with heavy hail", "11d"),
}


def _wmo_label(code: Any) -> tuple[str, str, str]:
    try:
        key = int(code)
    except (TypeError, ValueError):
        return ("Unknown", "unknown conditions", "01d")
    return WMO_CODES.get(key, ("Clouds", f"weather code {key}", "03d"))


def _fallback_weather(city: str) -> WeatherResponse:
    """Last-resort demo weather."""
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    current = WeatherDay(
        date=today,
        temp_min=18.0,
        temp_max=28.0,
        temperature=24.0,
        weather="Clear",
        description="clear sky (demo data)",
        humidity=55.0,
        wind=3.5,
        rain_chance=10.0,
        icon="01d",
    )
    forecast = [
        WeatherDay(
            date=today,
            temp_min=17.0 + i,
            temp_max=27.0 + i,
            temperature=22.0 + i,
            weather="Clouds" if i % 2 else "Clear",
            description="demo forecast",
            humidity=50.0 + i,
            wind=3.0 + i * 0.2,
            rain_chance=5.0 + i * 3,
            icon="02d" if i % 2 else "01d",
        )
        for i in range(5)
    ]
    return WeatherResponse(city=city, country=None, current=current, forecast=forecast)


def _rain_chance(item: dict[str, Any]) -> float:
    if "pop" in item:
        return round(float(item["pop"]) * 100, 1)
    rain = item.get("rain") or {}
    if isinstance(rain, dict):
        volume = rain.get("3h") or rain.get("1h") or 0
        return min(100.0, round(float(volume) * 20, 1))
    return 0.0


def _map_openweather_current(city: str, data: dict[str, Any]) -> WeatherResponse:
    main = data.get("main") or {}
    weather0 = (data.get("weather") or [{}])[0]
    wind = data.get("wind") or {}
    sys = data.get("sys") or {}
    current = WeatherDay(
        date=datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        temp_min=float(main.get("temp_min", 0)),
        temp_max=float(main.get("temp_max", 0)),
        temperature=float(main.get("temp", 0)),
        weather=weather0.get("main", "Unknown"),
        description=weather0.get("description", ""),
        humidity=float(main.get("humidity", 0)),
        wind=float(wind.get("speed", 0)),
        rain_chance=_rain_chance(data),
        icon=weather0.get("icon"),
    )
    return WeatherResponse(
        city=data.get("name") or city,
        country=sys.get("country"),
        current=current,
        forecast=[],
    )


async def _fetch_openweather(client: httpx.AsyncClient, city: str, api_key: str) -> WeatherResponse:
    params = {"q": city, "appid": api_key, "units": "metric"}
    current_resp = await client.get(f"{OPENWEATHER_BASE}/weather", params=params)
    current_resp.raise_for_status()
    current_data = current_resp.json()

    forecast_resp = await client.get(f"{OPENWEATHER_BASE}/forecast", params=params)
    forecast_resp.raise_for_status()
    forecast_data = forecast_resp.json()

    result = _map_openweather_current(city, current_data)

    by_date: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for item in forecast_data.get("list", []):
        date_key = (item.get("dt_txt") or "")[:10]
        if date_key:
            by_date[date_key].append(item)

    days: list[WeatherDay] = []
    for date_key in sorted(by_date.keys())[:5]:
        slots = by_date[date_key]
        temps = [float((s.get("main") or {}).get("temp", 0)) for s in slots]
        humidity = [float((s.get("main") or {}).get("humidity", 0)) for s in slots]
        winds = [float((s.get("wind") or {}).get("speed", 0)) for s in slots]
        rains = [_rain_chance(s) for s in slots]
        mid = slots[len(slots) // 2]
        weather0 = (mid.get("weather") or [{}])[0]
        days.append(
            WeatherDay(
                date=date_key,
                temp_min=min(temps) if temps else 0,
                temp_max=max(temps) if temps else 0,
                temperature=sum(temps) / len(temps) if temps else 0,
                weather=weather0.get("main", "Unknown"),
                description=weather0.get("description", ""),
                humidity=sum(humidity) / len(humidity) if humidity else 0,
                wind=sum(winds) / len(winds) if winds else 0,
                rain_chance=max(rains) if rains else 0,
                icon=weather0.get("icon"),
            )
        )
    result.forecast = days
    return result


async def _geocode_city(
    client: httpx.AsyncClient, city: str
) -> Optional[tuple[float, float, str, Optional[str]]]:
    """Return (lat, lon, display_name, country_code)."""
    resp = await client.get(
        NOMINATIM_URL,
        params={"q": city, "format": "json", "limit": 1, "addressdetails": 1},
        headers=HTTP_HEADERS,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    item = results[0]
    address = item.get("address") or {}
    country = address.get("country_code")
    country = country.upper() if isinstance(country, str) else None
    name = (
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("state")
        or city
    )
    return float(item["lat"]), float(item["lon"]), str(name), country


async def _fetch_open_meteo(client: httpx.AsyncClient, city: str) -> WeatherResponse:
    geo = await _geocode_city(client, city)
    if not geo:
        raise RuntimeError(f"Could not geocode city for weather: {city}")
    lat, lon, name, country = geo

    resp = await client.get(
        OPEN_METEO_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": (
                "temperature_2m,relative_humidity_2m,weather_code,"
                "wind_speed_10m,precipitation_probability"
            ),
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,wind_speed_10m_max"
            ),
            "timezone": "auto",
            "forecast_days": 5,
            "wind_speed_unit": "ms",
        },
        headers=HTTP_HEADERS,
    )
    resp.raise_for_status()
    data = resp.json()

    current_raw = data.get("current") or {}
    daily = data.get("daily") or {}
    weather, description, icon = _wmo_label(current_raw.get("weather_code"))

    # Pair current day min/max from daily[0] when available
    temps_max = daily.get("temperature_2m_max") or []
    temps_min = daily.get("temperature_2m_min") or []
    current = WeatherDay(
        date=(current_raw.get("time") or datetime.now(timezone.utc).isoformat())[:10],
        temp_min=float(temps_min[0]) if temps_min else float(current_raw.get("temperature_2m", 0)),
        temp_max=float(temps_max[0]) if temps_max else float(current_raw.get("temperature_2m", 0)),
        temperature=float(current_raw.get("temperature_2m", 0)),
        weather=weather,
        description=description,
        humidity=float(current_raw.get("relative_humidity_2m", 0)),
        wind=float(current_raw.get("wind_speed_10m", 0)),
        rain_chance=float(current_raw.get("precipitation_probability") or 0),
        icon=icon,
    )

    forecast: list[WeatherDay] = []
    dates = daily.get("time") or []
    codes = daily.get("weather_code") or []
    rains = daily.get("precipitation_probability_max") or []
    winds = daily.get("wind_speed_10m_max") or []
    for i, date_key in enumerate(dates[:5]):
        w_label, w_desc, w_icon = _wmo_label(codes[i] if i < len(codes) else 0)
        tmin = float(temps_min[i]) if i < len(temps_min) else 0
        tmax = float(temps_max[i]) if i < len(temps_max) else 0
        forecast.append(
            WeatherDay(
                date=date_key,
                temp_min=tmin,
                temp_max=tmax,
                temperature=round((tmin + tmax) / 2, 1),
                weather=w_label,
                description=w_desc,
                humidity=float(current.humidity),
                wind=float(winds[i]) if i < len(winds) else 0,
                rain_chance=float(rains[i]) if i < len(rains) else 0,
                icon=w_icon,
            )
        )

    return WeatherResponse(
        city=name,
        country=country,
        current=current,
        forecast=forecast,
    )


async def fetch_weather(city: str) -> WeatherResponse:
    """
    Fetch current weather + 5-day forecast.
    Tries OpenWeather first (if key set), then Open-Meteo.
    """
    api_key = get_env("OPENWEATHER_API_KEY")

    async with httpx.AsyncClient(timeout=25.0) as client:
        if api_key:
            try:
                result = await _fetch_openweather(client, city, api_key)
                logger.info("Weather source: OpenWeather for %s", city)
                return result
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "OpenWeather failed for %s (%s) — trying Open-Meteo", city, exc
                )

        try:
            result = await _fetch_open_meteo(client, city)
            logger.info("Weather source: Open-Meteo for %s", city)
            return result
        except Exception as exc:  # noqa: BLE001
            logger.exception("Open-Meteo failed for %s: %s", city, exc)
            return _fallback_weather(city)
