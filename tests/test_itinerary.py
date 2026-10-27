"""Unit tests for trip planning and itinerary generation."""

import pytest
from datetime import date
from src.trip_planner import TripPlanner


@pytest.fixture
def planner():
    return TripPlanner()


def test_itinerary_structure_and_duration(planner):
    start = date(2026, 12, 1)
    plan = planner.generate_itinerary(
        destination_id="IND_GOA_016",
        start_date=start,
        duration_days=4,
        travelers_count=2,
        pace="Balanced",
        travel_style="Moderate"
    )
    assert plan["destination_name"] == "Goa"
    assert plan["duration_days"] == 4
    assert len(plan["days"]) == 4

    for day in plan["days"]:
        assert "day_number" in day
        assert "theme" in day
        assert "activities" in day
        assert len(day["activities"]) >= 2
        # Check time slots are present
        slots = [a["slot"] for a in day["activities"]]
        assert "Morning" in slots
        assert "Afternoon" in slots


def test_relaxed_vs_packed_pace(planner):
    start = date(2026, 12, 1)
    plan_relaxed = planner.generate_itinerary(
        destination_id="IND_MUM_015",
        start_date=start,
        duration_days=2,
        pace="Relaxed"
    )
    plan_packed = planner.generate_itinerary(
        destination_id="IND_MUM_015",
        start_date=start,
        duration_days=2,
        pace="Packed"
    )

    # Packed pace has evening activity plus lunch break
    assert len(plan_packed["days"][0]["activities"]) >= len(plan_relaxed["days"][0]["activities"])


def test_invalid_destination_or_duration(planner):
    with pytest.raises(ValueError):
        planner.generate_itinerary(
            destination_id="NON_EXISTENT_999",
            start_date=date(2026, 12, 1),
            duration_days=3
        )

    with pytest.raises(ValueError):
        planner.generate_itinerary(
            destination_id="IND_DEL_001",
            start_date=date(2026, 12, 1),
            duration_days=0
        )
