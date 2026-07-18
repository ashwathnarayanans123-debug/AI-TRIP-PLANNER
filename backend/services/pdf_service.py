"""
PDF itinerary export using ReportLab.
"""

from __future__ import annotations

import io
import json
from typing import Any, Optional

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from models import Trip
from utils.helpers import from_json


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "TripTitle",
        parent=base["Heading1"],
        fontSize=20,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#0f766e"),
        spaceAfter=12,
    )
    heading = ParagraphStyle(
        "SectionHead",
        parent=base["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#134e4a"),
        spaceBefore=14,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "BodyTextCustom",
        parent=base["BodyText"],
        fontSize=10,
        leading=14,
        alignment=TA_LEFT,
    )
    small = ParagraphStyle(
        "SmallText",
        parent=base["BodyText"],
        fontSize=9,
        leading=12,
        textColor=colors.HexColor("#334155"),
    )
    return title, heading, body, small


def _bullet_list(items: list[Any], style) -> list:
    flowables = []
    for item in items:
        if isinstance(item, dict):
            name = item.get("name", "")
            phone = item.get("phone", "")
            notes = item.get("notes", "")
            text = f"• <b>{name}</b> — {phone}"
            if notes:
                text += f" ({notes})"
        else:
            text = f"• {item}"
        flowables.append(Paragraph(text, style))
    return flowables


def build_trip_pdf(trip: Trip) -> bytes:
    """
    Render a saved trip into a downloadable PDF byte stream.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=trip.title or "Trip Itinerary",
    )

    # Use the saved currency, fall back to INR if missing
    currency = (trip.currency or "INR").upper()

    title_style, heading_style, body_style, small_style = _styles()
    story: list = []

    story.append(Paragraph(trip.title or "Trip Itinerary", title_style))
    story.append(
        Paragraph(
            f"<b>From:</b> {trip.starting_location} &nbsp;&nbsp; "
            f"<b>To:</b> {trip.destination}",
            body_style,
        )
    )
    story.append(
        Paragraph(
            f"<b>Days:</b> {trip.number_of_days} &nbsp;&nbsp; "
            f"<b>Travelers:</b> {trip.number_of_travelers} &nbsp;&nbsp; "
            f"<b>Budget:</b> {trip.budget} &nbsp;&nbsp; "
            f"<b>Transport:</b> {trip.transportation}",
            small_style,
        )
    )
    if trip.start_date or trip.end_date:
        story.append(
            Paragraph(
                f"<b>Dates:</b> {trip.start_date or '—'} → {trip.end_date or '—'}",
                small_style,
            )
        )
    story.append(Spacer(1, 10))

    if trip.overview:
        story.append(Paragraph("Overview", heading_style))
        story.append(Paragraph(trip.overview, body_style))

    if trip.estimated_total_budget is not None:
        story.append(Paragraph("Estimated Total Budget", heading_style))
        story.append(
            Paragraph(
                f"{currency} {trip.estimated_total_budget:,.2f}",
                body_style,
            )
        )

    breakdown = from_json(trip.budget_breakdown_json, {}) or {}
    if breakdown:
        story.append(Paragraph("Budget Breakdown", heading_style))
        rows = [["Category", f"Amount ({currency})"]]
        for key in (
            "accommodation",
            "food",
            "transportation",
            "tickets",
            "shopping",
            "miscellaneous",
        ):
            if key in breakdown:
                rows.append([key.title(), f"{currency} {float(breakdown[key]):,.2f}"])
        table = Table(rows, colWidths=[3.5 * inch, 2 * inch])
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#0f766e")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#94a3b8")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0fdfa")]),
                    ("LEFTPADDING", (0, 0), (-1, -1), 8),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                    ("TOPPADDING", (0, 0), (-1, -1), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ]
            )
        )
        story.append(table)

    itinerary = from_json(trip.itinerary_json, []) or []
    if itinerary:
        story.append(Paragraph("Day-by-Day Itinerary", heading_style))
        for day in itinerary:
            day_num = day.get("day", "?")
            day_title = day.get("title") or f"Day {day_num}"
            story.append(Paragraph(f"<b>Day {day_num}: {day_title}</b>", body_style))
            if day.get("hotel"):
                story.append(Paragraph(f"Hotel: {day['hotel']}", small_style))
            for slot in ("morning", "afternoon", "evening"):
                segment = day.get(slot)
                if not segment:
                    continue
                activity = segment.get("activity", "")
                place = segment.get("place") or ""
                cost = segment.get("estimated_cost")
                cost_txt = f" (~{currency} {cost:,.0f})" if cost is not None else ""
                story.append(
                    Paragraph(
                        f"<b>{slot.title()}:</b> {activity}"
                        + (f" @ {place}" if place else "")
                        + cost_txt,
                        small_style,
                    )
                )
            nearby = day.get("nearby_attractions") or []
            if nearby:
                story.append(
                    Paragraph("Nearby: " + ", ".join(nearby), small_style)
                )
            story.append(Spacer(1, 6))

    # Hotel recommendations
    hotels = from_json(trip.hotel_recommendations_json, []) or []
    if hotels:
        story.append(Paragraph("Hotel Recommendations", heading_style))
        story.extend(_bullet_list(hotels, small_style))

    # Restaurant suggestions
    restaurants = from_json(trip.restaurant_suggestions_json, []) or []
    if restaurants:
        story.append(Paragraph("Restaurant Suggestions", heading_style))
        story.extend(_bullet_list(restaurants, small_style))

    for label, raw in (
        ("Packing Checklist", trip.packing_checklist_json),
        ("Safety Tips", trip.safety_tips_json),
        ("Hidden Gems", trip.hidden_gems_json),
        ("Travel Hacks", trip.travel_hacks_json),
    ):
        items = from_json(raw, []) or []
        if items:
            story.append(Paragraph(label, heading_style))
            story.extend(_bullet_list(items, small_style))

    contacts = from_json(trip.emergency_contacts_json, []) or []
    if contacts:
        story.append(Paragraph("Emergency Contacts", heading_style))
        story.extend(_bullet_list(contacts, small_style))

    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes
