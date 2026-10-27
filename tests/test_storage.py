"""Unit tests for SQLite trip storage and persistence."""

import pytest
from src.trip_storage import (
    save_trip,
    get_all_trips,
    get_trip_by_id,
    update_trip_title,
    delete_trip,
    clear_all_trips
)


@pytest.fixture(autouse=True)
def clean_database():
    clear_all_trips()
    yield
    clear_all_trips()


def test_save_and_retrieve_trip():
    itinerary = {
        "destination_name": "Jaipur",
        "days": [{"day_number": 1, "theme": "Forts"}]
    }
    budget = {"total_estimated_cost_inr": 24000.0}

    trip_id = save_trip(
        destination_id="IND_JAI_003",
        destination_name="Jaipur",
        start_date="2026-11-15",
        duration_days=3,
        travelers_count=2,
        itinerary_data=itinerary,
        budget_data=budget,
        custom_title="Royal Jaipur Expedition"
    )

    assert trip_id.startswith("TRIP_")

    retrieved = get_trip_by_id(trip_id)
    assert retrieved is not None
    assert retrieved["title"] == "Royal Jaipur Expedition"
    assert retrieved["duration_days"] == 3
    assert retrieved["total_cost_inr"] == 24000.0
    assert retrieved["itinerary"]["destination_name"] == "Jaipur"


def test_update_and_delete_trip():
    trip_id = save_trip(
        destination_id="IND_GOA_016",
        destination_name="Goa",
        start_date="2026-12-01",
        duration_days=4,
        travelers_count=1,
        itinerary_data={"days": []}
    )

    assert update_trip_title(trip_id, "Relaxing Goa Holiday") is True
    updated = get_trip_by_id(trip_id)
    assert updated["title"] == "Relaxing Goa Holiday"

    assert delete_trip(trip_id) is True
    assert get_trip_by_id(trip_id) is None
