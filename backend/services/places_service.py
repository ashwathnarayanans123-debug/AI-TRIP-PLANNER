"""
Free maps / places via OpenStreetMap stack:

  - Nominatim  → geocode destination to lat/lng
  - Overpass   → nearby hotels, restaurants, attractions

No API key required. Falls back to demo POIs (with real center) if Overpass is down.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

import httpx

from schemas import PlaceItem, PlacesResponse

logger = logging.getLogger(__name__)

NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
OVERPASS_ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
]

# Nominatim requires a descriptive User-Agent
HTTP_HEADERS = {
    "User-Agent": "WanderAI-TripPlanner/1.0 (educational; contact=hello@wanderai.app)",
    "Accept": "application/json",
}


def _offset_demo_pois(
    destination: str, center: dict[str, float]
) -> tuple[list[PlaceItem], list[PlaceItem], list[PlaceItem]]:
    """Demo POIs anchored around a real geocoded center."""
    lat, lng = center["lat"], center["lng"]
    hotels = [
        PlaceItem(
            name=f"Grand Stay {destination}",
            address=f"Central {destination}",
            lat=lat + 0.012,
            lng=lng + 0.01,
            types=["lodging"],
        ),
        PlaceItem(
            name=f"Boutique Inn {destination}",
            address=f"Old Town {destination}",
            lat=lat - 0.008,
            lng=lng + 0.006,
            types=["lodging"],
        ),
    ]
    restaurants = [
        PlaceItem(
            name=f"Local Flavors — {destination}",
            address=f"Food street, {destination}",
            lat=lat + 0.004,
            lng=lng - 0.007,
            types=["restaurant"],
        ),
        PlaceItem(
            name=f"Sunset Bistro — {destination}",
            address=f"Riverside, {destination}",
            lat=lat - 0.005,
            lng=lng - 0.004,
            types=["restaurant"],
        ),
    ]
    attractions = [
        PlaceItem(
            name=f"Heritage Landmark — {destination}",
            address=f"Historic quarter, {destination}",
            lat=lat + 0.007,
            lng=lng + 0.003,
            types=["tourist_attraction"],
        ),
        PlaceItem(
            name=f"Scenic Viewpoint — {destination}",
            address=f"Hillside, {destination}",
            lat=lat - 0.011,
            lng=lng + 0.009,
            types=["tourist_attraction"],
        ),
    ]
    return hotels, restaurants, attractions


def _demo_places(destination: str) -> PlacesResponse:
    center = {"lat": 15.2993, "lng": 74.1240}  # Goa-ish default if geocode fails
    hotels, restaurants, attractions = _offset_demo_pois(destination, center)
    return PlacesResponse(
        destination=destination,
        center=center,
        hotels=hotels,
        restaurants=restaurants,
        attractions=attractions,
    )


def _element_coords(el: dict[str, Any]) -> Optional[tuple[float, float]]:
    if "lat" in el and "lon" in el:
        return float(el["lat"]), float(el["lon"])
    center = el.get("center") or {}
    if "lat" in center and "lon" in center:
        return float(center["lat"]), float(center["lon"])
    return None


def _map_overpass_element(el: dict[str, Any], default_type: str) -> Optional[PlaceItem]:
    tags = el.get("tags") or {}
    name = tags.get("name")
    if not name:
        return None
    coords = _element_coords(el)
    if not coords:
        return None
    lat, lng = coords
    address_parts = [
        tags.get("addr:housenumber"),
        tags.get("addr:street"),
        tags.get("addr:city") or tags.get("addr:place"),
    ]
    address = ", ".join(p for p in address_parts if p) or tags.get("addr:full")
    return PlaceItem(
        name=name,
        address=address,
        place_id=str(el.get("id")),
        lat=lat,
        lng=lng,
        types=[default_type],
    )


async def _geocode_nominatim(
    client: httpx.AsyncClient, destination: str
) -> Optional[dict[str, float]]:
    resp = await client.get(
        NOMINATIM_URL,
        params={"q": destination, "format": "json", "limit": 1},
        headers=HTTP_HEADERS,
    )
    resp.raise_for_status()
    results = resp.json()
    if not results:
        return None
    return {"lat": float(results[0]["lat"]), "lng": float(results[0]["lon"])}


def _overpass_query(lat: float, lng: float, radius: int = 3000) -> str:
    """Compact Overpass QL — nodes only for speed."""
    return f"""
[out:json][timeout:20];
(
  node["tourism"="hotel"](around:{radius},{lat},{lng});
  node["amenity"="restaurant"](around:{radius},{lat},{lng});
  node["tourism"="attraction"](around:{radius},{lat},{lng});
  node["tourism"="museum"](around:{radius},{lat},{lng});
);
out body 30;
""".strip()


def _classify_element(el: dict[str, Any]) -> Optional[str]:
    tags = el.get("tags") or {}
    tourism = tags.get("tourism")
    amenity = tags.get("amenity")
    if tourism in {"hotel", "guest_house", "hostel", "motel"}:
        return "hotel"
    if amenity in {"restaurant", "cafe", "fast_food"}:
        return "restaurant"
    if tourism in {"attraction", "museum", "viewpoint"}:
        return "attraction"
    return None


async def _fetch_overpass(
    client: httpx.AsyncClient, lat: float, lng: float
) -> tuple[list[PlaceItem], list[PlaceItem], list[PlaceItem]]:
    """Try several Overpass mirrors until one succeeds."""
    query = _overpass_query(lat, lng)
    last_error: Optional[Exception] = None

    for url in OVERPASS_ENDPOINTS:
        try:
            resp = await client.post(
                url,
                content=query,
                headers={**HTTP_HEADERS, "Content-Type": "text/plain"},
                timeout=22.0,
            )
            if resp.status_code >= 400:
                logger.warning("Overpass %s returned %s", url, resp.status_code)
                continue
            elements = (resp.json() or {}).get("elements") or []
            hotels: list[PlaceItem] = []
            restaurants: list[PlaceItem] = []
            attractions: list[PlaceItem] = []
            seen: set[str] = set()

            for el in elements:
                category = _classify_element(el)
                if not category:
                    continue
                item = _map_overpass_element(el, category)
                if not item:
                    continue
                key = f"{item.name}|{item.lat}|{item.lng}"
                if key in seen:
                    continue
                seen.add(key)
                if category == "hotel" and len(hotels) < 8:
                    hotels.append(item)
                elif category == "restaurant" and len(restaurants) < 8:
                    restaurants.append(item)
                elif category == "attraction" and len(attractions) < 8:
                    attractions.append(item)

            return hotels, restaurants, attractions
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            logger.warning("Overpass mirror failed (%s): %s", url, exc)

    if last_error:
        raise last_error
    return [], [], []


def _filter_response(
    destination: str,
    center: dict[str, float],
    hotels: list[PlaceItem],
    restaurants: list[PlaceItem],
    attractions: list[PlaceItem],
    place_type: Optional[str],
) -> PlacesResponse:
    if place_type == "hotel":
        return PlacesResponse(destination=destination, center=center, hotels=hotels)
    if place_type == "restaurant":
        return PlacesResponse(
            destination=destination, center=center, restaurants=restaurants
        )
    if place_type == "tourist_attraction":
        return PlacesResponse(
            destination=destination, center=center, attractions=attractions
        )
    return PlacesResponse(
        destination=destination,
        center=center,
        hotels=hotels,
        restaurants=restaurants,
        attractions=attractions,
    )


async def fetch_places(destination: str, place_type: Optional[str] = None) -> PlacesResponse:
    """Geocode with Nominatim and load nearby places with Overpass."""
    try:
        async with httpx.AsyncClient(timeout=40.0) as client:
            center = await _geocode_nominatim(client, destination)
            if not center:
                logger.warning("Nominatim found no results for %s", destination)
                return _demo_places(destination)

            try:
                hotels, restaurants, attractions = await _fetch_overpass(
                    client, center["lat"], center["lng"]
                )
            except Exception as exc:  # noqa: BLE001
                logger.warning(
                    "Overpass unavailable for %s (%s) — using demo POIs at real center",
                    destination,
                    exc,
                )
                hotels, restaurants, attractions = _offset_demo_pois(destination, center)

            if not hotels and not restaurants and not attractions:
                hotels, restaurants, attractions = _offset_demo_pois(destination, center)

            return _filter_response(
                destination, center, hotels, restaurants, attractions, place_type
            )
    except Exception as exc:  # noqa: BLE001
        logger.exception("OSM places fetch failed for %s: %s", destination, exc)
        return _demo_places(destination)
