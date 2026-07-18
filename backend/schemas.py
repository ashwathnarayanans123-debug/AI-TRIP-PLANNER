"""
Pydantic schemas for request validation and API responses.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class BudgetLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    LUXURY = "luxury"


class TransportationType(str, Enum):
    CAR = "car"
    FLIGHT = "flight"
    TRAIN = "train"
    BUS = "bus"


class HotelType(str, Enum):
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


ALLOWED_INTERESTS = {
    "adventure",
    "mountains",
    "beaches",
    "nature",
    "wildlife",
    "shopping",
    "food",
    "temples",
    "history",
    "museums",
    "nightlife",
    "photography",
}


# ---------------------------------------------------------------------------
# Trip planning
# ---------------------------------------------------------------------------


class TripPlanRequest(BaseModel):
    """Input payload for POST /plan-trip."""

    starting_location: str = Field(..., min_length=2, max_length=255)
    destination: str = Field(..., min_length=2, max_length=255)
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    number_of_days: int = Field(..., ge=1, le=30)
    number_of_travelers: int = Field(..., ge=1, le=50)
    budget: BudgetLevel = BudgetLevel.MEDIUM
    transportation: TransportationType = TransportationType.FLIGHT
    hotel_type: HotelType = HotelType.STANDARD
    interests: list[str] = Field(default_factory=list)
    additional_notes: Optional[str] = Field(default=None, max_length=2000)
    user_id: Optional[int] = None

    @field_validator("interests")
    @classmethod
    def validate_interests(cls, values: list[str]) -> list[str]:
        cleaned: list[str] = []
        for item in values:
            key = item.strip().lower()
            if key and key in ALLOWED_INTERESTS:
                cleaned.append(key)
        return cleaned

    @field_validator("starting_location", "destination")
    @classmethod
    def strip_locations(cls, value: str) -> str:
        return value.strip()


class DaySegment(BaseModel):
    """Morning / afternoon / evening block."""

    time_of_day: str
    activity: str
    place: Optional[str] = None
    restaurant: Optional[str] = None
    estimated_cost: Optional[float] = None
    local_transport: Optional[str] = None
    best_visiting_time: Optional[str] = None
    notes: Optional[str] = None


class DayItinerary(BaseModel):
    day: int
    title: Optional[str] = None
    morning: Optional[DaySegment] = None
    afternoon: Optional[DaySegment] = None
    evening: Optional[DaySegment] = None
    hotel: Optional[str] = None
    nearby_attractions: list[str] = Field(default_factory=list)


class BudgetBreakdown(BaseModel):
    accommodation: float = 0.0
    food: float = 0.0
    transportation: float = 0.0
    tickets: float = 0.0
    shopping: float = 0.0
    miscellaneous: float = 0.0


class TripPlanResponse(BaseModel):
    """AI-generated trip plan returned by POST /plan-trip."""

    overview: str
    itinerary: list[DayItinerary]
    hotel_recommendations: list[str] = Field(default_factory=list)
    restaurant_suggestions: list[str] = Field(default_factory=list)
    packing_checklist: list[str] = Field(default_factory=list)
    safety_tips: list[str] = Field(default_factory=list)
    hidden_gems: list[str] = Field(default_factory=list)
    travel_hacks: list[str] = Field(default_factory=list)
    emergency_contacts: list[dict[str, str]] = Field(default_factory=list)
    estimated_total_budget: float = 0.0
    budget_breakdown: BudgetBreakdown = Field(default_factory=BudgetBreakdown)
    currency: str = "INR"


class SaveTripRequest(BaseModel):
    """Persist a planned trip via POST /save-trip."""

    starting_location: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    number_of_days: int = Field(..., ge=1, le=30)
    number_of_travelers: int = Field(..., ge=1, le=50)
    budget: BudgetLevel = BudgetLevel.MEDIUM
    transportation: TransportationType = TransportationType.FLIGHT
    hotel_type: HotelType = HotelType.STANDARD
    interests: list[str] = Field(default_factory=list)
    additional_notes: Optional[str] = None
    title: Optional[str] = None
    overview: Optional[str] = None
    itinerary: Optional[list[dict[str, Any]]] = None
    estimated_total_budget: Optional[float] = None
    currency: Optional[str] = "INR"
    budget_breakdown: Optional[BudgetBreakdown] = None
    hotel_recommendations: Optional[list[str]] = None
    restaurant_suggestions: Optional[list[str]] = None
    packing_checklist: Optional[list[str]] = None
    safety_tips: Optional[list[str]] = None
    hidden_gems: Optional[list[str]] = None
    travel_hacks: Optional[list[str]] = None
    emergency_contacts: Optional[list[dict[str, str]]] = None
    user_id: Optional[int] = None
    label: Optional[str] = None


class TripUpdateRequest(BaseModel):
    """Partial update for editing a saved trip."""

    title: Optional[str] = None
    starting_location: Optional[str] = None
    destination: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    number_of_days: Optional[int] = Field(default=None, ge=1, le=30)
    number_of_travelers: Optional[int] = Field(default=None, ge=1, le=50)
    budget: Optional[BudgetLevel] = None
    transportation: Optional[TransportationType] = None
    hotel_type: Optional[HotelType] = None
    interests: Optional[list[str]] = None
    additional_notes: Optional[str] = None
    overview: Optional[str] = None
    itinerary: Optional[list[dict[str, Any]]] = None
    estimated_total_budget: Optional[float] = None
    currency: Optional[str] = None
    budget_breakdown: Optional[BudgetBreakdown] = None
    hotel_recommendations: Optional[list[str]] = None
    restaurant_suggestions: Optional[list[str]] = None
    is_favorite: Optional[bool] = None


class TripSummary(BaseModel):
    id: int
    title: str
    starting_location: str
    destination: str
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    number_of_days: int
    number_of_travelers: int
    budget: str
    transportation: str
    hotel_type: str
    estimated_total_budget: Optional[float] = None
    currency: Optional[str] = "INR"
    is_favorite: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TripDetail(TripSummary):
    interests: Optional[str] = None
    additional_notes: Optional[str] = None
    overview: Optional[str] = None
    itinerary_json: Optional[str] = None
    budget_breakdown_json: Optional[str] = None
    hotel_recommendations_json: Optional[str] = None
    restaurant_suggestions_json: Optional[str] = None
    packing_checklist_json: Optional[str] = None
    safety_tips_json: Optional[str] = None
    hidden_gems_json: Optional[str] = None
    travel_hacks_json: Optional[str] = None
    emergency_contacts_json: Optional[str] = None

    model_config = {"from_attributes": True}


class SaveTripResponse(BaseModel):
    message: str
    trip: TripDetail


class HistoryResponse(BaseModel):
    total: int
    trips: list[TripSummary]


# ---------------------------------------------------------------------------
# Weather & Places
# ---------------------------------------------------------------------------


class WeatherRequest(BaseModel):
    city: str = Field(..., min_length=2, max_length=255)


class WeatherDay(BaseModel):
    date: str
    temp_min: float
    temp_max: float
    temperature: float
    weather: str
    description: str
    humidity: float
    wind: float
    rain_chance: float
    icon: Optional[str] = None


class WeatherResponse(BaseModel):
    city: str
    country: Optional[str] = None
    current: WeatherDay
    forecast: list[WeatherDay] = Field(default_factory=list)


class PlacesRequest(BaseModel):
    destination: str = Field(..., min_length=2, max_length=255)
    type: Optional[str] = Field(
        default="tourist_attraction",
        description="hotel | restaurant | tourist_attraction",
    )


class PlaceItem(BaseModel):
    name: str
    address: Optional[str] = None
    rating: Optional[float] = None
    place_id: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    types: list[str] = Field(default_factory=list)


class PlacesResponse(BaseModel):
    destination: str
    center: Optional[dict[str, float]] = None
    hotels: list[PlaceItem] = Field(default_factory=list)
    restaurants: list[PlaceItem] = Field(default_factory=list)
    attractions: list[PlaceItem] = Field(default_factory=list)


class MessageResponse(BaseModel):
    message: str
    id: Optional[int] = None
