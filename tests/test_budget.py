"""Unit tests for travel budget and cost calculations."""

import pytest
from pydantic import ValidationError
from src.budget_calculator import BudgetCalculator
from src.data_validation import BudgetRequestSchema


@pytest.fixture
def calculator():
    return BudgetCalculator()


def test_single_vs_multiple_travelers(calculator):
    req_single = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=1,
        num_days=3,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_single = calculator.calculate_trip_budget(req_single)

    req_double = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=2,
        num_days=3,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_double = calculator.calculate_trip_budget(req_double)

    # Transportation and food double; accommodation for 2 shares 1 room so stays identical
    assert res_double["breakdown"]["Total Transportation"] == 2 * res_single["breakdown"]["Total Transportation"]
    assert res_double["breakdown"]["Food & Dining"] == 2 * res_single["breakdown"]["Food & Dining"]
    assert res_double["breakdown"]["Accommodation"] == res_single["breakdown"]["Accommodation"]
    assert res_double["total_estimated_cost_inr"] > res_single["total_estimated_cost_inr"]


def test_one_day_trip_zero_nights(calculator):
    # 1-day day trip
    req = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=1,
        num_days=1,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=5.0
    )
    res = calculator.calculate_trip_budget(req)
    assert res["num_nights"] == 0
    assert res["breakdown"]["Accommodation"] == 0.0


def test_contingency_calculation(calculator):
    req = BudgetRequestSchema(
        destination_id="IND_DEL_001",
        starting_location="Delhi",
        num_travelers=1,
        num_days=2,
        transport_mode="Local Public Transit",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Walking & Public Transit",
        activities_level="Free & Self-Guided",
        contingency_percent=15.0
    )
    res = calculator.calculate_trip_budget(req)
    subtotal = res["subtotal_inr"]
    contingency = res["breakdown"]["Contingency Reserve"]
    expected_contingency = subtotal * 0.15
    assert abs(contingency - expected_contingency) < 0.01


def test_budget_shortfall_analysis(calculator):
    req = BudgetRequestSchema(
        destination_id="INT_PAR_020",
        starting_location="Delhi",
        num_travelers=2,
        num_days=5,
        transport_mode="Flight",
        accommodation_tier="5-Star Luxury Resort",
        food_tier="Fine Dining & Multi-Cuisine",
        local_transport_tier="Chauffeured Private Car",
        activities_level="All-Inclusive & Adventure Sports",
        contingency_percent=10.0,
        user_target_budget=50000.0  # Much too low for 5-star Paris luxury trip
    )
    res = calculator.calculate_trip_budget(req)
    sf = res["shortfall_analysis"]
    assert not sf["is_sufficient"]
    assert sf["status"] == "Budget Shortfall"
    assert sf["shortfall_amount_inr"] > 0
    assert len(sf["suggestions"]) > 0


def test_negative_values_rejected():
    with pytest.raises(ValidationError):
        BudgetRequestSchema(
            destination_id="IND_DEL_001",
            starting_location="Delhi",
            num_travelers=-1,  # Invalid
            num_days=3,
            transport_mode="Flight",
            accommodation_tier="Budget Hotel / Guesthouse",
            food_tier="Casual Dining & Cafes",
            local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
            activities_level="Moderate Sightseeing",
            contingency_percent=10.0
        )
