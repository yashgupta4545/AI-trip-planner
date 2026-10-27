"""Unit tests for trip export services (PDF, CSV, JSON)."""

import json
from datetime import date
from src.trip_planner import TripPlanner
from src.export_service import (
    export_trip_to_pdf,
    export_itinerary_to_csv,
    export_trip_to_json,
    export_budget_to_csv,
    export_budget_to_pdf
)


def test_pdf_generation():
    planner = TripPlanner()
    itinerary = planner.generate_itinerary("IND_JAI_003", date(2026, 11, 20), 2)
    budget = {
        "breakdown": {"Transportation": 4000.0, "Accommodation": 6000.0},
        "total_estimated_cost_inr": 10000.0,
        "per_person_cost_inr": 10000.0
    }

    pdf_bytes = export_trip_to_pdf(itinerary, budget)
    assert isinstance(pdf_bytes, bytes)
    assert len(pdf_bytes) > 1000
    # PDF magic byte signature %PDF-
    assert pdf_bytes.startswith(b"%PDF-")


def test_csv_export():
    planner = TripPlanner()
    itinerary = planner.generate_itinerary("IND_DEL_001", date(2026, 11, 20), 2)
    csv_str = export_itinerary_to_csv(itinerary)
    assert isinstance(csv_str, str)
    lines = csv_str.strip().split("\n")
    assert len(lines) >= 5
    assert "Day Number,Date,Day Theme" in lines[0]


def test_json_export():
    planner = TripPlanner()
    itinerary = planner.generate_itinerary("IND_GOA_016", date(2026, 11, 20), 2)
    json_str = export_trip_to_json(itinerary)
    parsed = json.loads(json_str)
    assert parsed["destination_name"] == "Goa"
    assert parsed["duration_days"] == 2


def test_budget_csv_and_pdf_export():
    sample_budget = {
        "destination_name": "Jaipur",
        "country": "India",
        "origin_city": "Delhi",
        "num_days": 3,
        "num_travelers": 2,
        "total_estimated_cost_inr": 18000.0,
        "per_person_cost_inr": 9000.0,
        "breakdown": {
            "Outbound Travel": 1400.0,
            "Return Travel": 1400.0,
            "Accommodation": 5000.0,
            "Food & Dining": 4500.0,
            "Local Transportation": 1200.0,
            "Attractions & Sightseeing": 1500.0,
            "Miscellaneous & Shopping": 1200.0,
            "Contingency Reserve": 1800.0
        },
        "assumptions": ["AC Express train", "3-star hotel"]
    }
    csv_out = export_budget_to_csv(sample_budget)
    assert "TripGenie AI - Travel Budget Estimate" in csv_out
    assert "Jaipur" in csv_out
    assert "18000.0" in csv_out

    pdf_bytes = export_budget_to_pdf(sample_budget)
    assert isinstance(pdf_bytes, bytes)
    assert pdf_bytes.startswith(b"%PDF-")

