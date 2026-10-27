"""Comprehensive verification tests covering Scenarios 1 through 10
from Section 11 of the TripGenie AI Requirements.
"""

from datetime import date
import pytest

from src.budget_calculator import BudgetCalculator
from src.data_loader import get_all_destinations, get_attractions_for_destination, get_destination_by_id
from src.data_validation import BudgetRequestSchema
from src.route_service import calculate_journey_logistics, get_origin_coordinates
from src.trip_planner import TripPlanner


@pytest.fixture
def calculator():
    return BudgetCalculator()


@pytest.fixture
def planner():
    return TripPlanner()


# -------------------------------------------------------------------
# Scenario 1: A user plans a two-day trip within Jaipur (same city)
# -------------------------------------------------------------------
def test_scenario_1_same_city_trip_jaipur_to_jaipur(calculator, planner):
    req = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Jaipur",
        num_travelers=2,
        num_days=2,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res = calculator.calculate_trip_budget(req)
    
    route = res["route_logistics"]
    assert route["is_same_city"] is True
    # In same-city trips, intercity transit is not charged; only local intra-city transit
    assert route["transport_mode"] == "Local Transit"
    assert res["breakdown"]["Total Transportation"] == 300.0 * 2.0  # 150/pax outbound + 150/pax return
    assert "intra-city transit" in route["assumptions"].lower()

    # Verify Itinerary generation for same-city staycation
    plan = planner.generate_itinerary(
        destination_id="IND_JAI_003",
        start_date=date(2026, 11, 1),
        duration_days=2,
        travelers_count=2,
        origin_city="Jaipur"
    )
    assert plan["duration_days"] == 2
    assert "local transit" in plan["days"][0]["activities"][0]["description"].lower()


# -------------------------------------------------------------------
# Scenario 2: A user plans a five-day domestic trip starting from Delhi
# -------------------------------------------------------------------
def test_scenario_2_domestic_trip_delhi_origin(calculator, planner):
    req = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=2,
        num_days=5,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res = calculator.calculate_trip_budget(req)

    route = res["route_logistics"]
    assert route["is_same_city"] is False
    assert route["travel_distance_km"] > 200.0
    assert route["outbound_duration_hours"] >= 3.0
    assert res["num_nights"] == 4
    # Lodging assumes 1 room for 4 nights
    assert res["rooms_count"] == 1
    assert res["breakdown"]["Outbound Travel"] > 0
    assert res["breakdown"]["Return Travel"] > 0
    assert res["breakdown"]["Total Transportation"] == res["breakdown"]["Outbound Travel"] + res["breakdown"]["Return Travel"]


# -------------------------------------------------------------------
# Scenario 3: An international trip from Jaipur to Tokyo
# -------------------------------------------------------------------
def test_scenario_3_international_trip_jaipur_to_tokyo(calculator):
    req = BudgetRequestSchema(
        destination_id="INT_TYO_011",
        starting_location="Jaipur",
        num_travelers=2,
        num_days=5,
        transport_mode="Flight",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Walking & Public Transit",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res = calculator.calculate_trip_budget(req)

    assert res["country"] == "Japan"
    assert res["currency"] == "JPY"
    assert res["scope"] == "International"
    # Destination-specific lodging in Tokyo reflects Tokyo baseline (~9,500/night/room)
    assert res["breakdown"]["Accommodation"] == 9500.0 * 1 * 4  # 4 nights
    assert res["total_estimated_cost_inr"] > 100000.0

    # Overland guard check: If user picks Bus from Jaipur to Tokyo, system guards and uses flight
    req_bus = BudgetRequestSchema(
        destination_id="INT_TYO_011",
        starting_location="Jaipur",
        num_travelers=1,
        num_days=5,
        transport_mode="Intercity Bus",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Walking & Public Transit",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_bus = calculator.calculate_trip_budget(req_bus)
    assert "overland_warning" in res_bus["route_logistics"]
    assert res_bus["route_logistics"]["transport_mode"] == "Flight"


# -------------------------------------------------------------------
# Scenario 4: User has limited budget and wants destinations that fit
# -------------------------------------------------------------------
def test_scenario_4_budget_fit_and_shortfall_analysis(calculator):
    # Sufficient budget
    req_healthy = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=1,
        num_days=2,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0,
        user_target_budget=20000.0
    )
    res_healthy = calculator.calculate_trip_budget(req_healthy)
    sf_healthy = res_healthy["shortfall_analysis"]
    assert sf_healthy["is_sufficient"] is True
    assert sf_healthy["status"] == "Healthy Budget"

    # Extremely constrained budget triggering shortfall alert with actionable suggestions
    req_tight = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=2,
        num_days=4,
        transport_mode="Train (Express / AC)",
        accommodation_tier="5-Star Luxury Resort",
        food_tier="Fine Dining & Multi-Cuisine",
        local_transport_tier="Chauffeured Private Car",
        activities_level="All-Inclusive & Adventure Sports",
        contingency_percent=10.0,
        user_target_budget=5000.0
    )
    res_tight = calculator.calculate_trip_budget(req_tight)
    sf_tight = res_tight["shortfall_analysis"]
    assert sf_tight["is_sufficient"] is False
    assert sf_tight["status"] == "Budget Shortfall"
    assert sf_tight["shortfall_amount_inr"] > 0
    assert len(sf_tight["suggestions"]) >= 2


# -------------------------------------------------------------------
# Scenario 5: User compares two destinations with different costs
# -------------------------------------------------------------------
def test_scenario_5_compare_destinations_with_different_costs(calculator):
    # Destination 1: Jaipur (Budget/Moderate Domestic)
    req_jai = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="Delhi",
        num_travelers=2,
        num_days=3,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_jai = calculator.calculate_trip_budget(req_jai)

    # Destination 2: Paris (International Luxury Hub)
    req_par = BudgetRequestSchema(
        destination_id="INT_PAR_020",
        starting_location="Delhi",
        num_travelers=2,
        num_days=3,
        transport_mode="Flight",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_par = calculator.calculate_trip_budget(req_par)

    # Costs must differ meaningfully based on destination economics
    assert res_par["total_estimated_cost_inr"] > 3 * res_jai["total_estimated_cost_inr"]
    assert res_par["breakdown"]["Accommodation"] > 2 * res_jai["breakdown"]["Accommodation"]
    assert res_par["currency"] == "EUR"
    assert res_jai["currency"] == "INR"


# -------------------------------------------------------------------
# Scenario 6: User changes the number of travelers
# -------------------------------------------------------------------
def test_scenario_6_change_number_of_travelers(calculator):
    req_1 = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=1,
        num_days=2,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_1 = calculator.calculate_trip_budget(req_1)

    req_4 = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=4,
        num_days=2,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res_4 = calculator.calculate_trip_budget(req_4)

    # Per person transit scales linearly
    assert res_4["breakdown"]["Total Transportation"] == 4 * res_1["breakdown"]["Total Transportation"]
    # Food scales linearly with 4 people
    assert res_4["breakdown"]["Food & Dining"] == 4 * res_1["breakdown"]["Food & Dining"]
    # 4 people require ceil(4/2) = 2 rooms, exactly double the 1 room needed for 1 person
    assert res_4["rooms_count"] == 2
    assert res_4["breakdown"]["Accommodation"] == 2 * res_1["breakdown"]["Accommodation"]

    # Personal vehicle group sharing test
    req_pv_1 = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=1,
        num_days=2,
        transport_mode="Personal Vehicle / Car",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Walking & Public Transit",
        activities_level="Free & Self-Guided",
        contingency_percent=0.0
    )
    req_pv_4 = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=4,
        num_days=2,
        transport_mode="Personal Vehicle / Car",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Walking & Public Transit",
        activities_level="Free & Self-Guided",
        contingency_percent=0.0
    )
    res_pv_1 = calculator.calculate_trip_budget(req_pv_1)
    res_pv_4 = calculator.calculate_trip_budget(req_pv_4)
    # Personal vehicle fuel and toll costs are shared by the car group, not multiplied per person
    assert res_pv_1["breakdown"]["Total Transportation"] == res_pv_4["breakdown"]["Total Transportation"]


# -------------------------------------------------------------------
# Scenario 7: User changes the trip duration
# -------------------------------------------------------------------
def test_scenario_7_change_trip_duration(calculator):
    # 1-day day-trip
    req_1d = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=1,
        num_days=1,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=0.0
    )
    res_1d = calculator.calculate_trip_budget(req_1d)
    assert res_1d["num_nights"] == 0
    assert res_1d["breakdown"]["Accommodation"] == 0.0

    # 4-day trip
    req_4d = BudgetRequestSchema(
        destination_id="IND_AGR_002",
        starting_location="Delhi",
        num_travelers=1,
        num_days=4,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Mid-range 3-Star Hotel",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=0.0
    )
    res_4d = calculator.calculate_trip_budget(req_4d)
    assert res_4d["num_nights"] == 3
    # 3 nights lodging
    assert res_4d["breakdown"]["Accommodation"] == 2200.0 * 3


# -------------------------------------------------------------------
# Scenario 8: Attraction verified vs estimated price status
# -------------------------------------------------------------------
def test_scenario_8_attraction_price_status_and_sources():
    attrs_agra = get_attractions_for_destination("IND_AGR_002")
    taj_mahal = next(a for a in attrs_agra if "taj mahal" in a["attraction_name"].lower())
    assert taj_mahal["price_status"] == "Verified"
    assert taj_mahal["adult_ticket_price"] == 50.0
    assert taj_mahal["child_ticket_price"] == 0.0
    assert "asi" in taj_mahal["source_name"].lower()

    # Free attractions are verified
    delhi_attrs = get_attractions_for_destination("IND_DEL_001")
    india_gate = next(a for a in delhi_attrs if "india gate" in a["attraction_name"].lower())
    assert india_gate["price_status"] == "Verified"
    assert india_gate["adult_ticket_price"] == 0.0


# -------------------------------------------------------------------
# Scenario 9: Route with unknown starting town falls back safely
# -------------------------------------------------------------------
def test_scenario_9_route_with_unknown_origin_fallback(calculator):
    # Origin town not in major list
    req_remote = BudgetRequestSchema(
        destination_id="IND_JAI_003",
        starting_location="SmallVillageXyz",
        num_travelers=1,
        num_days=3,
        transport_mode="Train (Express / AC)",
        accommodation_tier="Budget Hotel / Guesthouse",
        food_tier="Casual Dining & Cafes",
        local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
        activities_level="Moderate Sightseeing",
        contingency_percent=10.0
    )
    res = calculator.calculate_trip_budget(req_remote)
    # Does not crash; falls back gracefully to regional coordination hub
    assert res["total_estimated_cost_inr"] > 0
    assert res["route_logistics"]["origin_city"] == "SmallVillageXyz"


# -------------------------------------------------------------------
# Scenario 10: External booking searches and zero mandatory paid APIs
# -------------------------------------------------------------------
def test_scenario_10_external_booking_searches_and_offline_integrity():
    route = calculate_journey_logistics("Delhi", "IND_JAI_003", "Train (Express / AC)")
    links = route["search_links"]
    assert "Train Search (ConfirmTkt / IRCTC)" in links
    assert "https://www.confirmtkt.com" in links["Train Search (ConfirmTkt / IRCTC)"]
    assert "Hotel Search (Booking.com)" in links
    assert "Attractions Search (TripAdvisor)" in links

    # International routes produce flight searches
    intl_route = calculate_journey_logistics("Jaipur", "INT_TYO_011", "Flight")
    intl_links = intl_route["search_links"]
    assert "Flight Search (Google Flights)" in intl_links
    assert "https://www.google.com/travel/flights" in intl_links["Flight Search (Google Flights)"]
    assert "Flight Search (Skyscanner)" in intl_links
