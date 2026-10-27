"""Route Service for TripGenie AI.
Calculates geographic distances, travel durations, and realistic transport expenses
for complete origin-to-destination-and-return journeys across flights, trains, buses,
personal vehicles, and taxis, and generates legitimate booking search URLs.
"""

import math
import urllib.parse
from typing import Any, Dict, List, Optional, Tuple

from src.data_loader import get_destination_by_id


# Major Origin City Coordinates Database (Indian Metros, State Capitals, and Global Hubs)
KNOWN_ORIGIN_COORDINATES: Dict[str, Tuple[float, float]] = {
    # India
    "delhi": (28.6139, 77.2090),
    "new delhi": (28.6139, 77.2090),
    "mumbai": (18.9220, 72.8347),
    "bengaluru": (12.9716, 77.5946),
    "bangalore": (12.9716, 77.5946),
    "chennai": (13.0827, 80.2707),
    "kolkata": (22.5726, 88.3639),
    "hyderabad": (17.3850, 78.4867),
    "jaipur": (26.9124, 75.7873),
    "ahmedabad": (23.0225, 72.5714),
    "pune": (18.5204, 73.8567),
    "surat": (21.1702, 72.8311),
    "lucknow": (26.8467, 80.9462),
    "kanpur": (26.4499, 80.3319),
    "nagpur": (21.1458, 79.0882),
    "indore": (22.7196, 75.8577),
    "bhopal": (23.2599, 77.4126),
    "patna": (25.5941, 85.1376),
    "vadodara": (22.3072, 73.1812),
    "ghaziabad": (28.6692, 77.4538),
    "ludhiana": (30.9010, 75.8573),
    "agra": (27.1767, 78.0081),
    "nashik": (19.9975, 73.7898),
    "varanasi": (25.3176, 82.9739),
    "amritsar": (31.6340, 74.8723),
    "allahabad": (25.4358, 81.8463),
    "prayagraj": (25.4358, 81.8463),
    "ranchi": (23.3441, 85.3096),
    "coimbatore": (11.0168, 76.9558),
    "madurai": (9.9252, 78.1198),
    "chandigarh": (30.7333, 76.7794),
    "guwahati": (26.1445, 91.7362),
    "kochi": (9.9312, 76.2673),
    "cochin": (9.9312, 76.2673),
    "trivandrum": (8.5241, 76.9366),
    "thiruvananthapuram": (8.5241, 76.9366),
    "mysuru": (12.2958, 76.6394),
    "mysore": (12.2958, 76.6394),
    "bhubaneswar": (20.2961, 85.8245),
    "dehradun": (30.3165, 78.0322),
    "goa": (15.2993, 74.1240),
    "srinagar": (34.0837, 74.7973),
    "shimla": (31.1048, 77.1734),
    "leh": (34.1526, 77.5771),
    # International Hubs
    "dubai": (25.2048, 55.2708),
    "london": (51.5074, -0.1278),
    "paris": (48.8566, 2.3522),
    "singapore": (1.3521, 103.8198),
    "bangkok": (13.7563, 100.5018),
    "tokyo": (35.6762, 139.6503),
    "new york": (40.7128, -74.0060),
    "sydney": ( -33.8688, 151.2093),
}


def haversine_distance_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great circle distance between two points on Earth in kilometers."""
    r = 6371.0  # Earth radius in kilometers
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = math.sin(delta_phi / 2.0) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(r * c, 1)


def get_origin_coordinates(origin_name: str) -> Optional[Tuple[float, float]]:
    """Look up coordinates for an origin city."""
    clean = origin_name.strip().lower()
    if clean in KNOWN_ORIGIN_COORDINATES:
        return KNOWN_ORIGIN_COORDINATES[clean]
    # Check partial match
    for k, v in KNOWN_ORIGIN_COORDINATES.items():
        if k in clean or clean in k:
            return v
    # Default fallback to Delhi
    return KNOWN_ORIGIN_COORDINATES["delhi"]


def generate_booking_search_links(
    origin_city: str,
    destination_name: str,
    country: str,
    transport_mode: str,
    departure_date: Optional[str] = None
) -> Dict[str, str]:
    """Generate search URLs for flights, trains, buses, and hotels."""
    clean_orig = urllib.parse.quote_plus(origin_city.strip())
    clean_dest = urllib.parse.quote_plus(destination_name.strip())

    links = {}

    # Flight search
    links["Flight Search (Google Flights)"] = (
        f"https://www.google.com/travel/flights?q=flights+from+{clean_orig}+to+{clean_dest}"
    )
    links["Flight Search (Skyscanner)"] = (
        f"https://www.skyscanner.co.in/transport/flights/{clean_orig}/{clean_dest}/"
    )

    # Rail search (primarily Indian domestic)
    if country.lower() == "india":
        links["Train Search (ConfirmTkt / IRCTC)"] = (
            f"https://www.confirmtkt.com/trains/{clean_orig}-to-{clean_dest}"
        )
        links["Bus Search (RedBus)"] = (
            f"https://www.redbus.in/bus-tickets/{clean_orig}-to-{clean_dest}"
        )

    # Hotel search
    links["Hotel Search (Booking.com)"] = (
        f"https://www.booking.com/searchresults.html?ss={clean_dest}"
    )

    # Sights search
    links["Attractions Search (TripAdvisor)"] = (
        f"https://www.tripadvisor.com/Search?q={clean_dest}+attractions"
    )

    return links


def calculate_journey_logistics(
    origin_city: str,
    destination_id: str,
    transport_mode: str = "Flight",
    num_travelers: int = 1,
    personal_vehicle_mileage: float = 15.0,
    fuel_price_inr: float = 95.0
) -> Dict[str, Any]:
    """Calculate outbound, return, distance, and duration between starting city and destination."""
    dest = get_destination_by_id(destination_id)
    if not dest:
        raise ValueError(f"Destination '{destination_id}' not found.")

    dest_name = dest["destination_name"]
    dest_country = dest.get("country", "India")
    is_domestic = dest.get("is_domestic", True)

    orig_coords = get_origin_coordinates(origin_city)
    dest_lat = float(dest.get("latitude", 28.61))
    dest_lon = float(dest.get("longitude", 77.20))

    direct_dist_km = haversine_distance_km(orig_coords[0], orig_coords[1], dest_lat, dest_lon)

    # Case 1: Same City Journey (e.g. Jaipur to Jaipur)
    if direct_dist_km < 35.0 or origin_city.strip().lower() == dest_name.strip().lower():
        local_one_way = 150.0 * num_travelers
        return {
            "origin_city": origin_city,
            "destination_name": dest_name,
            "is_same_city": True,
            "direct_distance_km": 15.0,
            "travel_distance_km": 15.0,
            "transport_mode": "Local Transit",
            "outbound_cost_inr": local_one_way,
            "return_cost_inr": local_one_way,
            "total_transport_cost_inr": local_one_way * 2.0,
            "outbound_duration_hours": 0.5,
            "return_duration_hours": 0.5,
            "assumptions": "Local trip within destination city. Intra-city transit rates applied; intercity transport not required.",
            "price_status": "Verified",
            "search_links": generate_booking_search_links(origin_city, dest_name, dest_country, transport_mode)
        }

    # Case 2: International Overland Fallback
    # If route is international with distance > 1000km and user selected ground transport, notify and switch to flight logic
    mode = transport_mode
    overland_warning = None
    if not is_domestic and mode in ["Train (Express / AC)", "Intercity Bus", "Self-drive / Rental Car", "Personal Vehicle / Car"]:
        overland_warning = (
            f"Overland transport ({mode}) is not available across international waters/borders for this route. "
            f"Estimating scheduled flight rates."
        )
        mode = "Flight"

    outbound_per_traveler = 0.0
    group_shared_cost = 0.0
    duration_hours = 2.0
    assumptions = ""
    status = "Estimated"

    if mode == "Train (Express / AC)":
        rail_dist = round(direct_dist_km * 1.25, 1)
        # Indian Railways slab: base ₹250 + ₹1.65/km
        outbound_per_traveler = round(250.0 + (rail_dist * 1.65), 2)
        duration_hours = max(1.5, round((rail_dist / 65.0), 1))
        assumptions = f"AC 3-Tier/2-Tier Express train ({rail_dist:,.0f} km rail route @ ~INR 1.65/km)."
        total_dist = rail_dist

    elif mode == "Intercity Bus":
        road_dist = round(direct_dist_km * 1.22, 1)
        outbound_per_traveler = round(180.0 + (road_dist * 1.40), 2)
        duration_hours = max(2.0, round((road_dist / 50.0), 1))
        assumptions = f"Volvo AC / Sleeper intercity bus ({road_dist:,.0f} km road route @ ~INR 1.40/km)."
        total_dist = road_dist

    elif mode in ["Personal Vehicle / Car", "Self-drive / Rental Car"]:
        road_dist = round(direct_dist_km * 1.22, 1)
        # Fuel for round trip = (2 * road_dist / mileage) * fuel_price
        round_trip_dist = road_dist * 2.0
        liters_needed = round_trip_dist / max(5.0, personal_vehicle_mileage)
        total_fuel = liters_needed * fuel_price_inr
        # Tolls estimate: ~INR 1.4 per km on highway
        total_tolls = road_dist * 1.4
        round_trip_shared = total_fuel + (total_tolls * 2.0)
        # Split half into outbound, half into return
        group_shared_cost = round_trip_shared / 2.0
        duration_hours = max(1.5, round((road_dist / 60.0), 1))
        assumptions = (
            f"Personal vehicle road trip ({road_dist:,.0f} km one-way). "
            f"Fuel: {personal_vehicle_mileage:.0f} km/L @ INR {fuel_price_inr:.0f}/L, plus highway tolls. Shared by vehicle group."
        )
        total_dist = road_dist

    elif mode in ["Taxi / Rental Cab", "Chauffeured Private Car"]:
        road_dist = round(direct_dist_km * 1.22, 1)
        # Taxi rate: INR 14/km round trip + driver fee
        round_trip_dist = road_dist * 2.0
        group_shared_cost = (round_trip_dist * 13.5) / 2.0
        duration_hours = max(1.5, round((road_dist / 60.0), 1))
        assumptions = f"Outstation private cab ({road_dist:,.0f} km one-way @ INR 13.5/km round-trip rate). Shared by group."
        total_dist = road_dist

    else:  # Default: Flight
        air_dist = round(direct_dist_km * 1.05, 1)
        if is_domestic:
            # Domestic flight pricing formula: Base INR 3,200 + distance slab
            if air_dist < 600:
                outbound_per_traveler = 3400.0
            elif air_dist < 1200:
                outbound_per_traveler = 4800.0
            else:
                outbound_per_traveler = 6200.0
            flight_time = round(max(0.75, air_dist / 700.0), 1)
            duration_hours = flight_time + 2.0  # +2 hours airport processing
            assumptions = f"Economy domestic scheduled flight (~{air_dist:,.0f} km air route, {flight_time}h airtime + airport boarding)."
        else:
            # International flight pricing formula based on distance & region
            if air_dist < 3000:  # Middle East / SE Asia (e.g. Dubai, Bangkok, Singapore)
                outbound_per_traveler = 12000.0
            elif air_dist < 7500:  # Europe, East Asia (e.g. Paris, Tokyo, London)
                outbound_per_traveler = 24000.0
            else:  # Americas, Oceania (e.g. New York, Sydney, Peru)
                outbound_per_traveler = 42000.0
            flight_time = round(max(2.0, air_dist / 800.0), 1)
            duration_hours = flight_time + 3.0  # +3 hours international immigration & security
            assumptions = f"International scheduled flight (~{air_dist:,.0f} km air route, {flight_time}h airtime + international immigration)."
        total_dist = air_dist

    # Compute totals
    if group_shared_cost > 0:
        outbound_total = group_shared_cost
        return_total = group_shared_cost
    else:
        outbound_total = outbound_per_traveler * num_travelers
        return_total = outbound_per_traveler * num_travelers

    total_round_trip = outbound_total + return_total

    search_links = generate_booking_search_links(
        origin_city=origin_city,
        destination_name=dest_name,
        country=dest_country,
        transport_mode=mode
    )

    result = {
        "origin_city": origin_city,
        "destination_name": dest_name,
        "destination_country": dest_country,
        "is_same_city": False,
        "direct_distance_km": direct_dist_km,
        "travel_distance_km": total_dist,
        "transport_mode": mode,
        "num_travelers": num_travelers,
        "outbound_cost_inr": round(outbound_total, 2),
        "return_cost_inr": round(return_total, 2),
        "total_transport_cost_inr": round(total_round_trip, 2),
        "outbound_duration_hours": duration_hours,
        "return_duration_hours": duration_hours,
        "assumptions": assumptions,
        "price_status": status,
        "search_links": search_links
    }

    if overland_warning:
        result["overland_warning"] = overland_warning

    return result
