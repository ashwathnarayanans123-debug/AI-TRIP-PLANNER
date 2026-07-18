"""
AI trip planning engine powered by Groq (preferred) or OpenAI.

Generates a structured itinerary with overview, daily plans, budget,
packing list, safety tips, hidden gems, travel hacks, and emergency contacts.
Falls back to a deterministic template when no AI API key is set.
"""

from __future__ import annotations

import json
import logging
import re
from typing import Any, Optional

from openai import OpenAI

from schemas import (
    BudgetBreakdown,
    DayItinerary,
    DaySegment,
    TripPlanRequest,
    TripPlanResponse,
)
from utils.helpers import get_env

logger = logging.getLogger(__name__)

GROQ_BASE_URL = "https://api.groq.com/openai/v1"
DEFAULT_GROQ_MODEL = "llama-3.3-70b-versatile"
DEFAULT_OPENAI_MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are WanderAI, a senior travel designer who writes premium itineraries.
Return ONLY valid JSON matching the requested schema (no markdown, no commentary).

Quality rules:
- Use real, well-known place names for the destination (landmarks, neighborhoods, restaurants, hotels).
- Morning/afternoon/evening activities must be specific (not vague like "explore the city").
- Each activity string should be 1–2 vivid sentences with what to do and why.
- Costs must be realistic for the budget level and number of travelers.
- budget_breakdown values MUST add up exactly to estimated_total_budget.
- Use INR for all budget and cost values in this app.
- packing_checklist: at least 8 practical items.
- safety_tips, hidden_gems, travel_hacks: at least 4 each.
- hotel_recommendations and restaurant_suggestions: at least 3 each with real-sounding names.
- emergency_contacts: include local emergency number, tourist police/helpline, and medical tip.
- Keep day titles short and evocative.
"""


def _guess_currency(destination: str) -> str:
    dest = destination.lower()
    india = (
        "india",
        "delhi",
        "mumbai",
        "jaipur",
        "goa",
        "agra",
        "bengaluru",
        "bangalore",
        "chennai",
        "hyderabad",
        "kolkata",
        "kerala",
        "udaipur",
        "varanasi",
        "rishikesh",
        "manali",
        "shimla",
        "leh",
        "pondicherry",
        "pune",
    )
    if any(x in dest for x in india):
        return "INR"
    euro = (
        "france",
        "paris",
        "italy",
        "rome",
        "spain",
        "madrid",
        "barcelona",
        "germany",
        "berlin",
        "amsterdam",
        "portugal",
        "lisbon",
        "greece",
        "athens",
        "vienna",
        "ireland",
        "dublin",
    )
    if any(x in dest for x in euro):
        return "EUR"
    uk = ("london", "uk", "united kingdom", "england", "scotland", "wales")
    if any(x in dest for x in uk):
        return "GBP"
    japan = ("japan", "tokyo", "osaka", "kyoto")
    if any(x in dest for x in japan):
        return "JPY"
    return "INR"


def _build_user_prompt(req: TripPlanRequest) -> str:
    interests = ", ".join(req.interests) if req.interests else "general sightseeing"
    notes = req.additional_notes or "None"
    currency_hint = _guess_currency(req.destination)
    return f"""
Create a premium personalized trip plan.

Starting location: {req.starting_location}
Destination: {req.destination}
Start date: {req.start_date or "flexible"}
End date: {req.end_date or "flexible"}
Number of days: {req.number_of_days}
Travelers: {req.number_of_travelers}
Budget level: {req.budget.value}
Transportation to destination: {req.transportation.value}
Hotel type: {req.hotel_type.value}
Interests: {interests}
Additional notes: {notes}
Preferred currency: {currency_hint}

Return JSON with this exact structure:
{{
  "overview": "2-4 sentence engaging overview of the trip vibe and highlights",
  "itinerary": [
    {{
      "day": 1,
      "title": "short theme",
      "morning": {{
        "time_of_day": "morning",
        "activity": "detailed activity",
        "place": "specific place name",
        "restaurant": "breakfast/brunch suggestion or null",
        "estimated_cost": 0,
        "local_transport": "how to get there",
        "best_visiting_time": "e.g. 8:00 AM – 11:00 AM",
        "notes": "practical tip"
      }},
      "afternoon": {{ "time_of_day": "afternoon", "activity": "...", "place": "...", "restaurant": "...", "estimated_cost": 0, "local_transport": "...", "best_visiting_time": "...", "notes": "..." }},
      "evening": {{ "time_of_day": "evening", "activity": "...", "place": "...", "restaurant": "...", "estimated_cost": 0, "local_transport": "...", "best_visiting_time": "...", "notes": "..." }},
      "hotel": "named hotel recommendation for the night",
      "nearby_attractions": ["place 1", "place 2", "place 3"]
    }}
  ],
  "hotel_recommendations": ["Hotel A — area", "Hotel B — area", "Hotel C — area"],
  "restaurant_suggestions": ["Restaurant A — cuisine", "Restaurant B — cuisine", "Restaurant C — cuisine"],
  "packing_checklist": ["item1", "item2", "... at least 8"],
  "safety_tips": ["tip1", "... at least 4"],
  "hidden_gems": ["gem1", "... at least 4"],
  "travel_hacks": ["hack1", "... at least 4"],
  "emergency_contacts": [
    {{"name": "Emergency Services", "phone": "local number", "notes": "..."}},
    {{"name": "Tourist Helpline", "phone": "...", "notes": "..."}},
    {{"name": "Medical / Hospital tip", "phone": "...", "notes": "..."}}
  ],
  "estimated_total_budget": 0,
  "budget_breakdown": {{
    "accommodation": 0,
    "food": 0,
    "transportation": 0,
    "tickets": 0,
    "shopping": 0,
    "miscellaneous": 0
  }},
  "currency": "{currency_hint}"
}}

Hard requirements:
- Include exactly {req.number_of_days} days.
- Costs reflect {req.budget.value} budget for {req.number_of_travelers} traveler(s).
- estimated_total_budget MUST equal the sum of budget_breakdown.
- Do not invent impossible logistics; keep the plan walkable/doable for each day.
""".strip()


def _fallback_plan(req: TripPlanRequest) -> TripPlanResponse:
    """Deterministic demo itinerary when the LLM is unavailable."""
    budget_multipliers = {"low": 0.6, "medium": 1.0, "luxury": 2.2}
    mult = budget_multipliers.get(req.budget.value, 1.0)
    currency = _guess_currency(req.destination)
    unit = 9000.0
    base_per_day = unit * mult * req.number_of_travelers

    itinerary: list[DayItinerary] = []
    for day in range(1, req.number_of_days + 1):
        interest_hint = (
            req.interests[(day - 1) % len(req.interests)]
            if req.interests
            else "sightseeing"
        )
        itinerary.append(
            DayItinerary(
                day=day,
                title=f"Day {day}: Discover {req.destination} ({interest_hint})",
                morning=DaySegment(
                    time_of_day="morning",
                    activity=(
                        f"Start with a local breakfast, then visit a standout "
                        f"{interest_hint} spot in {req.destination}."
                    ),
                    place=f"Central {req.destination}",
                    restaurant=f"Local Cafe — {req.destination}",
                    estimated_cost=round(15 * mult * req.number_of_travelers * (unit / 120), 2),
                    local_transport="Walk / metro / auto",
                    best_visiting_time="8:00 AM – 11:00 AM",
                    notes="Arrive early to avoid crowds and heat.",
                ),
                afternoon=DaySegment(
                    time_of_day="afternoon",
                    activity=f"Hands-on {interest_hint} experience with a guided visit.",
                    place=f"{req.destination} highlights district",
                    restaurant=f"Regional Kitchen — {req.destination}",
                    estimated_cost=round(35 * mult * req.number_of_travelers * (unit / 120), 2),
                    local_transport=req.transportation.value,
                    best_visiting_time="12:00 PM – 4:00 PM",
                    notes="Book popular tickets online when possible.",
                ),
                evening=DaySegment(
                    time_of_day="evening",
                    activity="Catch sunset views and enjoy a memorable dinner.",
                    place=f"Evening district in {req.destination}",
                    restaurant=f"Recommended Bistro — {req.destination}",
                    estimated_cost=round(40 * mult * req.number_of_travelers * (unit / 120), 2),
                    local_transport="Taxi / rideshare",
                    best_visiting_time="5:30 PM – 9:00 PM",
                    notes="Keep valuables secure after dark.",
                ),
                hotel=f"{req.hotel_type.value.title()} stay near {req.destination} center",
                nearby_attractions=[
                    f"Main square — {req.destination}",
                    f"Local market — {req.destination}",
                    f"Scenic overlook — {req.destination}",
                ],
            )
        )

    total = round(base_per_day * req.number_of_days, 2)
    breakdown = BudgetBreakdown(
        accommodation=round(total * 0.35, 2),
        food=round(total * 0.25, 2),
        transportation=round(total * 0.20, 2),
        tickets=round(total * 0.10, 2),
        shopping=round(total * 0.05, 2),
        miscellaneous=round(total * 0.05, 2),
    )
    # Fix rounding drift
    breakdown.miscellaneous = round(
        total
        - (
            breakdown.accommodation
            + breakdown.food
            + breakdown.transportation
            + breakdown.tickets
            + breakdown.shopping
        ),
        2,
    )

    return TripPlanResponse(
        overview=(
            f"A curated {req.number_of_days}-day {req.budget.value} trip from "
            f"{req.starting_location} to {req.destination} for "
            f"{req.number_of_travelers} traveler(s), traveling by {req.transportation.value}."
        ),
        itinerary=itinerary,
        hotel_recommendations=[
            f"{req.hotel_type.value.title()} Hotel near downtown {req.destination}",
            f"Boutique stay in {req.destination}",
            f"Traveler-friendly lodge — {req.destination}",
        ],
        restaurant_suggestions=[
            f"Signature local restaurant — {req.destination}",
            f"Casual street-food lane — {req.destination}",
            f"Scenic dinner spot — {req.destination}",
        ],
        packing_checklist=[
            "Passport / government ID",
            "Comfortable walking shoes",
            "Weather-appropriate clothing",
            "Portable charger / power bank",
            "Reusable water bottle",
            "Travel adapter",
            "First-aid basics & personal meds",
            "Sunscreen / hat / light scarf",
            "Copies of bookings offline",
        ],
        safety_tips=[
            "Share your itinerary with someone trusted.",
            "Use licensed taxis or reputable rideshare apps.",
            "Keep digital and paper copies of important documents.",
            "Save local emergency numbers before you arrive.",
        ],
        hidden_gems=[
            f"Quiet neighborhood cafe in {req.destination}",
            f"Lesser-known viewpoint near {req.destination}",
            f"Local artisan market off the main street",
            f"Sunset lane popular with locals in {req.destination}",
        ],
        travel_hacks=[
            "Book popular attractions for early morning slots.",
            "Carry a small amount of local cash for markets.",
            "Download offline maps before arriving.",
            "Eat where locals queue — usually better value.",
        ],
        emergency_contacts=[
            {
                "name": "Local Emergency Services",
                "phone": "112 / 911",
                "notes": "Universal emergency number where available",
            },
            {
                "name": "Tourist Police / Helpline",
                "phone": "Ask hotel desk on arrival",
                "notes": f"Confirm local number in {req.destination}",
            },
            {
                "name": "Nearest major hospital",
                "phone": "Ask hotel concierge",
                "notes": "Save address offline",
            },
        ],
        estimated_total_budget=total,
        budget_breakdown=breakdown,
        currency=currency,
    )


def _parse_ai_json(content: str) -> dict[str, Any]:
    text = content.strip()
    if text.startswith("```"):
        lines = text.split("\n")
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        text = "\n".join(lines).strip()
        if text.lower().startswith("json"):
            text = text[4:].strip()
    # Recover if model wraps extra prose
    if not text.startswith("{"):
        match = re.search(r"\{.*\}", text, flags=re.DOTALL)
        if match:
            text = match.group(0)
    return json.loads(text)


def _ensure_list(values: Any, minimum: int, fillers: list[str]) -> list[str]:
    items = [str(v).strip() for v in (values or []) if str(v).strip()]
    for filler in fillers:
        if len(items) >= minimum:
            break
        if filler not in items:
            items.append(filler)
    return items


def _normalize_plan(data: dict[str, Any], req: TripPlanRequest) -> TripPlanResponse:
    """Validate, enrich thin sections, and reconcile budget totals."""
    days: list[DayItinerary] = []
    for item in data.get("itinerary") or []:
        days.append(DayItinerary.model_validate(item))

    # Pad missing days from fallback if model under-delivered
    if len(days) < req.number_of_days:
        fallback = _fallback_plan(req)
        existing = {d.day for d in days}
        for d in fallback.itinerary:
            if d.day not in existing and len(days) < req.number_of_days:
                days.append(d)
        days = sorted(days, key=lambda d: d.day)[: req.number_of_days]

    breakdown = BudgetBreakdown.model_validate(data.get("budget_breakdown") or {})
    total = float(data.get("estimated_total_budget") or 0)
    parts = [
        breakdown.accommodation,
        breakdown.food,
        breakdown.transportation,
        breakdown.tickets,
        breakdown.shopping,
        breakdown.miscellaneous,
    ]
    parts_sum = round(sum(parts), 2)

    if total <= 0 and parts_sum > 0:
        total = parts_sum
    elif parts_sum <= 0 and total > 0:
        breakdown = BudgetBreakdown(
            accommodation=round(total * 0.35, 2),
            food=round(total * 0.25, 2),
            transportation=round(total * 0.20, 2),
            tickets=round(total * 0.10, 2),
            shopping=round(total * 0.05, 2),
            miscellaneous=0,
        )
        breakdown.miscellaneous = round(
            total
            - (
                breakdown.accommodation
                + breakdown.food
                + breakdown.transportation
                + breakdown.tickets
                + breakdown.shopping
            ),
            2,
        )
    elif abs(parts_sum - total) > 1:
        # Prefer breakdown sum as source of truth when they disagree
        total = parts_sum

    currency = (data.get("currency") or _guess_currency(req.destination)).upper()

    packing = _ensure_list(
        data.get("packing_checklist"),
        8,
        [
            "Passport / government ID",
            "Comfortable walking shoes",
            "Weather-appropriate layers",
            "Portable charger",
            "Reusable water bottle",
            "Travel adapter",
            "Basic first-aid kit",
            "Sunscreen / hat",
        ],
    )
    safety = _ensure_list(
        data.get("safety_tips"),
        4,
        [
            "Share your live location with a trusted contact.",
            "Use licensed transport at night.",
            "Keep copies of IDs and bookings offline.",
            "Know the local emergency number.",
        ],
    )
    gems = _ensure_list(
        data.get("hidden_gems"),
        4,
        [
            f"Quiet cafe away from the main square in {req.destination}",
            f"Local craft market in {req.destination}",
            f"Sunset viewpoint known mainly to locals",
            f"Neighborhood walking lane with street snacks",
        ],
    )
    hacks = _ensure_list(
        data.get("travel_hacks"),
        4,
        [
            "Start landmark visits at opening time.",
            "Carry small cash for markets and tips.",
            "Download offline maps before you go.",
            "Keep one empty bag for souvenirs.",
        ],
    )
    hotels = _ensure_list(
        data.get("hotel_recommendations"),
        3,
        [
            f"{req.hotel_type.value.title()} hotel near city center",
            f"Boutique stay in {req.destination}",
            f"Well-reviewed lodge for {req.budget.value} travelers",
        ],
    )
    restaurants = _ensure_list(
        data.get("restaurant_suggestions"),
        3,
        [
            f"Signature local restaurant in {req.destination}",
            f"Popular street-food stretch",
            f"Scenic dinner spot",
        ],
    )

    contacts = data.get("emergency_contacts") or []
    if len(contacts) < 2:
        contacts = [
            {
                "name": "Local Emergency Services",
                "phone": "112",
                "notes": "Use local emergency number for your destination",
            },
            {
                "name": "Tourist Helpline",
                "phone": "Ask your hotel desk",
                "notes": "Confirm on arrival",
            },
            {
                "name": "Medical assistance",
                "phone": "Hotel concierge / nearest hospital",
                "notes": "Save address offline",
            },
        ]

    overview = (data.get("overview") or "").strip()
    if len(overview) < 40:
        overview = (
            f"A {req.number_of_days}-day {req.budget.value} escape from "
            f"{req.starting_location} to {req.destination}, built around "
            f"{', '.join(req.interests) if req.interests else 'local highlights'}."
        )

    return TripPlanResponse(
        overview=overview,
        itinerary=days,
        hotel_recommendations=hotels,
        restaurant_suggestions=restaurants,
        packing_checklist=packing,
        safety_tips=safety,
        hidden_gems=gems,
        travel_hacks=hacks,
        emergency_contacts=contacts,
        estimated_total_budget=float(total),
        budget_breakdown=breakdown,
        currency=currency,
    )


def _resolve_llm_client() -> tuple[Optional[OpenAI], Optional[str], Optional[str]]:
    groq_key = get_env("GROQ_API_KEY")
    if groq_key:
        model = get_env("GROQ_MODEL", DEFAULT_GROQ_MODEL)
        client = OpenAI(api_key=groq_key, base_url=GROQ_BASE_URL)
        return client, model, "groq"

    openai_key = get_env("OPENAI_API_KEY")
    if openai_key:
        model = get_env("OPENAI_MODEL", DEFAULT_OPENAI_MODEL)
        client = OpenAI(api_key=openai_key)
        return client, model, "openai"

    return None, None, None


def generate_trip_plan(req: TripPlanRequest) -> TripPlanResponse:
    """Generate a full trip plan via Groq/OpenAI, or use the local fallback."""
    client, model, provider = _resolve_llm_client()

    if not client or not model:
        logger.warning("No GROQ_API_KEY or OPENAI_API_KEY — using fallback itinerary")
        return _fallback_plan(req)

    try:
        logger.info("Generating trip plan with %s (%s)", provider, model)
        response = client.chat.completions.create(
            model=model,
            temperature=0.65,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_user_prompt(req)},
            ],
        )
        raw = response.choices[0].message.content or "{}"
        data = _parse_ai_json(raw)
        return _normalize_plan(data, req)
    except Exception as exc:  # noqa: BLE001
        logger.exception("%s planning failed, using fallback: %s", provider, exc)
        return _fallback_plan(req)
