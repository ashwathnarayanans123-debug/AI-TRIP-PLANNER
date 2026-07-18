"""
Trip planning, save, history, CRUD, duplicate, and PDF export routes.
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session

from database import get_db
from models import SavedTrip, Trip
from schemas import (
    HistoryResponse,
    MessageResponse,
    SaveTripRequest,
    SaveTripResponse,
    TripDetail,
    TripPlanRequest,
    TripPlanResponse,
    TripSummary,
    TripUpdateRequest,
)
from services.ai_planner import generate_trip_plan
from services.pdf_service import build_trip_pdf
from utils.helpers import (
    build_trip_title,
    interests_to_str,
    to_json,
)

router = APIRouter(tags=["trips"])

# ---------------------------------------------------------------------------
# Rate limiting — imported lazily so app still works if slowapi is not installed
# ---------------------------------------------------------------------------
try:
    from slowapi import Limiter
    from slowapi.util import get_remote_address
    from utils.helpers import get_env as _get_env

    _rate_limit = _get_env("PLAN_TRIP_RATE_LIMIT", "10/minute")
    limiter = Limiter(key_func=get_remote_address)
    _RATE_LIMITING = True
except ImportError:  # pragma: no cover
    limiter = None  # type: ignore[assignment]
    _RATE_LIMITING = False
    _rate_limit = "10/minute"


def _apply_plan_fields(trip: Trip, plan: TripPlanResponse) -> None:
    """Write all AI-generated fields from a TripPlanResponse onto a Trip ORM object."""
    trip.overview = plan.overview
    trip.itinerary_json = to_json([d.model_dump() for d in plan.itinerary])
    trip.estimated_total_budget = plan.estimated_total_budget
    trip.currency = plan.currency
    trip.budget_breakdown_json = to_json(plan.budget_breakdown.model_dump())
    trip.hotel_recommendations_json = to_json(plan.hotel_recommendations)
    trip.restaurant_suggestions_json = to_json(plan.restaurant_suggestions)
    trip.packing_checklist_json = to_json(plan.packing_checklist)
    trip.safety_tips_json = to_json(plan.safety_tips)
    trip.hidden_gems_json = to_json(plan.hidden_gems)
    trip.travel_hacks_json = to_json(plan.travel_hacks)
    trip.emergency_contacts_json = to_json(plan.emergency_contacts)


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@router.post("/plan-trip", response_model=TripPlanResponse)
def plan_trip(payload: TripPlanRequest, request: Request) -> TripPlanResponse:
    """Generate a personalized AI trip itinerary (rate-limited)."""
    if _RATE_LIMITING and limiter is not None:
        limiter.check()  # decorator approach used at app level; manual check as fallback
    return generate_trip_plan(payload)


@router.post("/save-trip", response_model=SaveTripResponse)
def save_trip(payload: SaveTripRequest, db: Session = Depends(get_db)) -> SaveTripResponse:
    """Persist a planned trip and create a SavedTrip history entry."""
    title = payload.title or build_trip_title(payload.destination, payload.number_of_days)

    trip = Trip(
        user_id=payload.user_id,
        title=title,
        starting_location=payload.starting_location,
        destination=payload.destination,
        start_date=payload.start_date,
        end_date=payload.end_date,
        number_of_days=payload.number_of_days,
        number_of_travelers=payload.number_of_travelers,
        budget=payload.budget.value if hasattr(payload.budget, "value") else payload.budget,
        transportation=(
            payload.transportation.value
            if hasattr(payload.transportation, "value")
            else payload.transportation
        ),
        hotel_type=(
            payload.hotel_type.value
            if hasattr(payload.hotel_type, "value")
            else payload.hotel_type
        ),
        interests=interests_to_str(payload.interests),
        additional_notes=payload.additional_notes,
        overview=payload.overview,
        itinerary_json=to_json(payload.itinerary) if payload.itinerary is not None else None,
        estimated_total_budget=payload.estimated_total_budget,
        currency=payload.currency or "INR",
        budget_breakdown_json=(
            to_json(payload.budget_breakdown.model_dump())
            if payload.budget_breakdown
            else None
        ),
        hotel_recommendations_json=(
            to_json(payload.hotel_recommendations)
            if payload.hotel_recommendations is not None
            else None
        ),
        restaurant_suggestions_json=(
            to_json(payload.restaurant_suggestions)
            if payload.restaurant_suggestions is not None
            else None
        ),
        packing_checklist_json=(
            to_json(payload.packing_checklist) if payload.packing_checklist is not None else None
        ),
        safety_tips_json=to_json(payload.safety_tips) if payload.safety_tips is not None else None,
        hidden_gems_json=to_json(payload.hidden_gems) if payload.hidden_gems is not None else None,
        travel_hacks_json=to_json(payload.travel_hacks) if payload.travel_hacks is not None else None,
        emergency_contacts_json=(
            to_json(payload.emergency_contacts)
            if payload.emergency_contacts is not None
            else None
        ),
    )
    db.add(trip)
    db.flush()

    saved = SavedTrip(
        user_id=payload.user_id,
        trip_id=trip.id,
        label=payload.label or title,
    )
    db.add(saved)
    db.flush()

    return SaveTripResponse(message="Trip saved successfully", trip=TripDetail.model_validate(trip))


@router.get("/history", response_model=HistoryResponse)
def get_history(
    q: Optional[str] = Query(default=None, description="Search destination or title"),
    user_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db),
) -> HistoryResponse:
    """List saved trips with optional search filter."""
    query = db.query(Trip)
    if user_id is not None:
        query = query.filter(Trip.user_id == user_id)
    if q:
        like = f"%{q.strip()}%"
        query = query.filter(
            (Trip.destination.ilike(like))
            | (Trip.title.ilike(like))
            | (Trip.starting_location.ilike(like))
        )
    trips = query.order_by(Trip.updated_at.desc()).all()
    return HistoryResponse(
        total=len(trips),
        trips=[TripSummary.model_validate(t) for t in trips],
    )


@router.get("/trip/{trip_id}", response_model=TripDetail)
def get_trip(trip_id: int, db: Session = Depends(get_db)) -> TripDetail:
    """Fetch a single trip by ID."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripDetail.model_validate(trip)


@router.put("/trip/{trip_id}", response_model=TripDetail)
def update_trip(
    trip_id: int,
    payload: TripUpdateRequest,
    db: Session = Depends(get_db),
) -> TripDetail:
    """Edit fields on an existing trip."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    data = payload.model_dump(exclude_unset=True)
    if "interests" in data and data["interests"] is not None:
        data["interests"] = interests_to_str(data["interests"])
    if "itinerary" in data and data["itinerary"] is not None:
        data["itinerary_json"] = to_json(data.pop("itinerary"))
    if "budget_breakdown" in data and data["budget_breakdown"] is not None:
        bb = data.pop("budget_breakdown")
        data["budget_breakdown_json"] = to_json(
            bb if isinstance(bb, dict) else bb.model_dump()
        )
    if "hotel_recommendations" in data and data["hotel_recommendations"] is not None:
        data["hotel_recommendations_json"] = to_json(data.pop("hotel_recommendations"))
    if "restaurant_suggestions" in data and data["restaurant_suggestions"] is not None:
        data["restaurant_suggestions_json"] = to_json(data.pop("restaurant_suggestions"))

    for key, value in data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(trip, key, value)

    db.flush()
    return TripDetail.model_validate(trip)


@router.delete("/trip/{trip_id}", response_model=MessageResponse)
def delete_trip(trip_id: int, db: Session = Depends(get_db)) -> MessageResponse:
    """Delete a trip and its saved-trip links."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    db.delete(trip)
    db.flush()
    return MessageResponse(message="Trip deleted", id=trip_id)


@router.post("/trip/{trip_id}/duplicate", response_model=SaveTripResponse)
def duplicate_trip(trip_id: int, db: Session = Depends(get_db)) -> SaveTripResponse:
    """Clone an existing trip for reuse."""
    original = db.query(Trip).filter(Trip.id == trip_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Trip not found")

    clone = Trip(
        user_id=original.user_id,
        title=f"{original.title} (Copy)",
        starting_location=original.starting_location,
        destination=original.destination,
        start_date=original.start_date,
        end_date=original.end_date,
        number_of_days=original.number_of_days,
        number_of_travelers=original.number_of_travelers,
        budget=original.budget,
        transportation=original.transportation,
        hotel_type=original.hotel_type,
        interests=original.interests,
        additional_notes=original.additional_notes,
        overview=original.overview,
        itinerary_json=original.itinerary_json,
        estimated_total_budget=original.estimated_total_budget,
        currency=original.currency,
        budget_breakdown_json=original.budget_breakdown_json,
        hotel_recommendations_json=original.hotel_recommendations_json,
        restaurant_suggestions_json=original.restaurant_suggestions_json,
        packing_checklist_json=original.packing_checklist_json,
        safety_tips_json=original.safety_tips_json,
        hidden_gems_json=original.hidden_gems_json,
        travel_hacks_json=original.travel_hacks_json,
        emergency_contacts_json=original.emergency_contacts_json,
        is_favorite=False,
    )
    db.add(clone)
    db.flush()

    saved = SavedTrip(
        user_id=clone.user_id,
        trip_id=clone.id,
        label=clone.title,
    )
    db.add(saved)
    db.flush()

    return SaveTripResponse(message="Trip duplicated", trip=TripDetail.model_validate(clone))


@router.post("/trip/{trip_id}/reuse", response_model=TripPlanResponse)
def reuse_trip(trip_id: int, db: Session = Depends(get_db)) -> TripPlanResponse:
    """
    Re-run the AI planner using the saved trip's original inputs.
    """
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    interests = [i for i in (trip.interests or "").split(",") if i]
    req = TripPlanRequest(
        starting_location=trip.starting_location,
        destination=trip.destination,
        start_date=trip.start_date,
        end_date=trip.end_date,
        number_of_days=trip.number_of_days,
        number_of_travelers=trip.number_of_travelers,
        budget=trip.budget,
        transportation=trip.transportation,
        hotel_type=trip.hotel_type,
        interests=interests,
        additional_notes=trip.additional_notes,
        user_id=trip.user_id,
    )
    plan = generate_trip_plan(req)
    _apply_plan_fields(trip, plan)
    db.flush()
    return plan


@router.get("/trip/{trip_id}/pdf")
def export_trip_pdf(trip_id: int, db: Session = Depends(get_db)) -> Response:
    """Download the itinerary as a PDF."""
    trip = db.query(Trip).filter(Trip.id == trip_id).first()
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    pdf_bytes = build_trip_pdf(trip)
    filename = f"trip_{trip_id}_{trip.destination.replace(' ', '_')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
