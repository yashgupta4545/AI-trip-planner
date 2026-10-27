# ✈️ TripGenie AI — Intelligent Travel Planning & Realistic Budget Platform

> **"Your Complete Journey. Realistic Destination Budgets. Unforgettable Adventures."**

TripGenie AI is an end-to-end travel planning web application supporting **326 verified destinations** across India and 70+ international countries. Built with **Python**, **Streamlit**, **Scikit-learn**, **Pandas**, **Folium**, and **ReportLab**, it features an **offline-first, zero-mandatory-paid-API architecture** with destination-specific pricing, complete origin-to-destination journey logistics, and a centralized budget calculator.

---

## 🌟 Four Major Enhancements

### 1. Destination-Specific & Attraction-Specific Pricing
* **Realistic Destination Economics**: Replaced uniform prices with real baseline costs for every destination (e.g. accommodation and meals in Jaipur realistically differ from Tokyo, Paris, Goa, or Leh).
* **Transparent Price Status**: Every price is explicitly tagged as `[Verified]` (obtained from official tourism departments/ASI/monument trusts) or `[Estimated]` (derived from documented regional tourism indices).
* **Granular Admissions**: Attractions support separate adult and child ticket prices, currencies (`INR`, `EUR`, `JPY`, `USD`, `GBP`, `AED`, etc.), and verified sources.

### 2. Complete Journey Planning (Origin ⇄ Destination)
* **Door-to-Door Route Logistics**: Calculates distance, travel duration, and transport costs from the user's starting location to the destination and back.
* **Multi-Modal Transport Support**:
  - **AC Express Trains**: Distance-based fare slabs with ConfirmTkt/IRCTC booking search links.
  - **Intercity Volvo/Sleeper Buses**: Distance-based highway rates with RedBus search links.
  - **Scheduled Flights**: Domestic & international route tiers with Google Flights and Skyscanner search links.
  - **Personal Vehicles**: Distance × 2 with fuel consumption based on user mileage (km/L), fuel price (INR/L), and highway tolls.
  - **Same-City Trips**: Detects when origin matches destination (e.g. Jaipur to Jaipur); intercity transport is ₹0 and local intra-city transit is used.
* **Arrival & Departure Itinerary**: Day 1 plans outbound departure, travel time, and hotel check-in; middle days plan attractions and meals; final day plans hotel check-out and return transit home.

### 3. Substantially Improved Explore Destinations
* **"Find Destinations Within Your Budget"**: Users enter starting location, total budget, travelers, and duration; the platform ranks destinations that fit comfortably and flags closest alternatives with shortfall notices if budget is tight.
* **Enhanced Destination Cards**: Display destination-specific daily expenses, lodging, round-trip transport from origin, estimated total trip cost, and `[Verified]` / `[Estimated]` status.
* **Detailed Budget Preview Drawer**: Itemizes journey, accommodation, dining, local transit, and sightseeing, with a direct **"Plan This Trip"** button that transfers all parameters into the AI Trip Planner.
* **Side-by-Side Comparison**: Select 2 to 4 destinations to compare transit, lodging, living costs, total trip expenses, and duration in an interactive table.

### 4. Centralized Trip Budget Calculator
* **Unified Cost Calculation**: Shared between Explore Destinations, AI Trip Planner, and Budget Calculator to guarantee consistent results.
* **10-Category Breakdown**: Outbound transit, Return transit, Accommodation, Dining, Local transit, Attraction tickets, Activities, Miscellaneous, Contingency reserve, and Per-Traveler cost.
* **Shortfall & Savings Advice**: Detects budget overages and suggests actionable alternatives (shorter duration, economical hotel tier, train over flight, free sights).
* **Triple Document Export**: Download estimates as structured CSV, JSON, or printable PDF.

---

## 📁 Project Structure

```
raghav/
├── app.py                      # Main landing page & platform statistics
├── requirements.txt            # Python dependencies
├── pytest.ini                  # Pytest configuration
├── README.md                   # Project documentation
├── DEMO_GUIDE.md               # Evaluator demonstration walkthrough
├── run_app.bat                 # One-click Windows launch script
├── setup_and_run.bat           # Environment setup & launcher
├── data/
│   ├── destinations.csv        # 326 destinations with destination-specific rates
│   ├── attractions.csv         # 1,291 attractions with adult/child tickets & sources
│   └── budget_estimates.csv    # Tier pricing multipliers
├── src/
│   ├── __init__.py
│   ├── config.py               # Constants, design tokens, and taxonomy
│   ├── data_validation.py      # Pydantic v2 schemas (Destination, Attraction, Budget)
│   ├── data_loader.py          # Cached data loading & search filters
│   ├── route_service.py        # Journey distances, durations, transit fares & booking links
│   ├── budget_calculator.py    # Centralized itemized cost calculator & shortfall analysis
│   ├── trip_planner.py         # Complete journey itinerary generator
│   ├── recommendation_engine.py# TF-IDF + Cosine similarity ML recommender
│   ├── weather_service.py      # Open-Meteo live forecast & offline fallback
│   ├── map_service.py          # Folium interactive mapping
│   ├── llm_service.py          # Optional LLM / local deterministic advice
│   ├── trip_storage.py         # SQLite persistence (trips.db)
│   └── export_service.py       # ReportLab PDF, CSV, and JSON export
├── pages/
│   ├── 1_Explore_Destinations.py # Budget discovery, cards, preview drawer & comparison
│   ├── 2_AI_Trip_Planner.py     # Complete journey itinerary with booking links
│   ├── 3_Budget_Calculator.py   # Centralized calculator with pie chart & exports
│   ├── 4_My_Trips.py            # Saved trips management (SQLite)
│   ├── 5_Weather_and_Maps.py    # Live weather forecasts & interactive maps
│   └── 6_About.py               # Methodology, ethics, and system architecture
├── scripts/
│   ├── import_destinations.py  # Dataset generator with verified/estimated prices
│   ├── validate_dataset.py     # Pydantic dataset validation
│   └── evaluate_recommendations.py # Persona evaluation benchmark
└── tests/
    ├── test_scenarios.py       # 10 dedicated scenario tests (Scenarios 1-10)
    ├── test_budget.py          # Centralized budget calculator tests
    ├── test_data_loader.py     # Dataset loader and search filter tests
    ├── test_exports.py         # PDF, CSV, and JSON export tests
    ├── test_itinerary.py       # Complete itinerary generator tests
    ├── test_recommendations.py # ML recommendation engine tests
    ├── test_storage.py         # SQLite persistence tests
    └── test_weather_fallback.py# Open-Meteo & offline fallback tests
```

---

## 🚀 Running the Application

### 1. Environment Setup
```powershell
cd c:\Users\yash8\raghav
.\.venv\Scripts\Activate.ps1
```

### 2. Validate Datasets
```powershell
python scripts/validate_dataset.py
```
*(Validates 326 destinations and 1,291 attractions against Pydantic schemas).*

### 3. Run Automated Tests
```powershell
python -m pytest -v
```
*(Runs 38 unit & integration tests covering all 10 evaluation scenarios with 100% pass rate).*

### 4. Launch Web Application
```powershell
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your browser.

---

## 🧪 Evaluation Scenarios (Section 11 Verification)

| Scenario | Description | Tested Component | Result |
| :--- | :--- | :--- | :--- |
| **Scenario 1** | 2-Day trip within Jaipur (same city) | `test_scenario_1_same_city_trip_jaipur_to_jaipur` | ✅ Passed (0 intercity fare, local transit applied) |
| **Scenario 2** | 5-Day domestic trip from Delhi | `test_scenario_2_domestic_trip_delhi_origin` | ✅ Passed (Outbound & return rail, 4 nights lodging) |
| **Scenario 3** | International trip from Jaipur to Tokyo | `test_scenario_3_international_trip_jaipur_to_tokyo` | ✅ Passed (Flight transit, JPY currency, Tokyo baseline lodging) |
| **Scenario 4** | Limited budget filtering & recommendations | `test_scenario_4_budget_fit_and_shortfall_analysis` | ✅ Passed (Surplus vs Shortfall alert & suggestions) |
| **Scenario 5** | Destination comparison (Jaipur vs Paris) | `test_scenario_5_compare_destinations_with_different_costs` | ✅ Passed (Realistic cost divergence, EUR vs INR) |
| **Scenario 6** | Traveler count changes (1 vs 4 travelers) | `test_scenario_6_change_number_of_travelers` | ✅ Passed (Per-person scaling, car fuel group sharing) |
| **Scenario 7** | Trip duration changes (1-day vs 4-day) | `test_scenario_7_change_trip_duration` | ✅ Passed (1-day has 0 nights, 4-day has 3 nights) |
| **Scenario 8** | Attraction verified vs estimated pricing | `test_scenario_8_attraction_price_status_and_sources` | ✅ Passed (Taj Mahal ASI verified, India Gate free) |
| **Scenario 9** | Unknown origin location fallback | `test_scenario_9_route_with_unknown_origin_fallback` | ✅ Passed (Graceful regional hub coordination) |
| **Scenario 10**| Free sources & external search links | `test_scenario_10_external_booking_searches_and_offline_integrity` | ✅ Passed (Google Flights, Skyscanner, IRCTC, RedBus) |
| **Total Automated Tests** | | **38 Tests** | **100% Success** |

---

## 📄 License & Attribution
TripGenie AI utilizes public geographic coordinates from OpenStreetMap and meteorological forecasts from Open-Meteo. Official attraction ticket prices are verified from the Archaeological Survey of India (ASI) and respective state tourism boards.
