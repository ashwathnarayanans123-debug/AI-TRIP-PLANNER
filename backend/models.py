"""
SQLAlchemy ORM models for the AI Trip Planner Agent.

Tables:
  - users: optional user identity for saved trips
  - trips: generated trip plans (full itinerary JSON)
  - saved_trips: bookmark / history association layer
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from database import Base


def _now() -> datetime:
    """Return current UTC time (timezone-aware, compatible with Python 3.12+)."""
    return datetime.now(timezone.utc)


class User(Base):
    """Application user (lightweight; expandable for auth later)."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=True, index=True)
    name = Column(String(150), nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    trips = relationship("Trip", back_populates="user", cascade="all, delete-orphan")
    saved_trips = relationship(
        "SavedTrip", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email={self.email!r}>"


class Trip(Base):
    """A generated AI trip plan with form inputs and full itinerary payload."""

    __tablename__ = "trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)

    # Form inputs
    title = Column(String(255), nullable=False, default="Untitled Trip")
    starting_location = Column(String(255), nullable=False)
    destination = Column(String(255), nullable=False, index=True)
    start_date = Column(String(50), nullable=True)
    end_date = Column(String(50), nullable=True)
    number_of_days = Column(Integer, nullable=False, default=3)
    number_of_travelers = Column(Integer, nullable=False, default=1)
    budget = Column(String(50), nullable=False, default="medium")  # low | medium | luxury
    transportation = Column(String(50), nullable=False, default="flight")
    hotel_type = Column(String(50), nullable=False, default="standard")
    interests = Column(Text, nullable=True)  # comma-separated or JSON string
    additional_notes = Column(Text, nullable=True)

    # AI-generated content stored as JSON strings
    itinerary_json = Column(Text, nullable=True)
    overview = Column(Text, nullable=True)
    estimated_total_budget = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True, default="INR")  # e.g. INR, EUR, USD
    budget_breakdown_json = Column(Text, nullable=True)
    hotel_recommendations_json = Column(Text, nullable=True)  # list[str] as JSON
    restaurant_suggestions_json = Column(Text, nullable=True)  # list[str] as JSON
    packing_checklist_json = Column(Text, nullable=True)
    safety_tips_json = Column(Text, nullable=True)
    hidden_gems_json = Column(Text, nullable=True)
    travel_hacks_json = Column(Text, nullable=True)
    emergency_contacts_json = Column(Text, nullable=True)

    # Metadata
    is_favorite = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=_now, onupdate=_now, nullable=False
    )

    user = relationship("User", back_populates="trips")
    saved_entries = relationship(
        "SavedTrip", back_populates="trip", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Trip id={self.id} destination={self.destination!r}>"


class SavedTrip(Base):
    """Explicit save / history record linking a user to a trip."""

    __tablename__ = "saved_trips"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    trip_id = Column(Integer, ForeignKey("trips.id"), nullable=False, index=True)
    label = Column(String(255), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=_now, nullable=False)

    user = relationship("User", back_populates="saved_trips")
    trip = relationship("Trip", back_populates="saved_entries")

    def __repr__(self) -> str:
        return f"<SavedTrip id={self.id} trip_id={self.trip_id}>"
