"""Transparent budget and travel expense calculator for TripGenie AI.
Computes itemized category breakdowns, contingency reserves, per-person rates,
and provides shortfall analysis with actionable saving recommendations.
Incorporates destination-specific baseline economics and origin-route logistics.
"""

import math
from typing import Any, Dict, List, Optional

from src.data_loader import get_attractions_for_destination, get_budget_estimates, get_destination_by_id
from src.data_validation import BudgetRequestSchema
from src.route_service import calculate_journey_logistics


# Tier Multipliers applied against destination-specific base economics
ACCOMMODATION_TIER_MULTIPLIERS = {
    "Hostel / Backpacker Pod": 0.35,
    "Budget Hotel / Guesthouse": 0.60,
    "Mid-range 3-Star Hotel": 1.00,
    "Boutique / 4-Star Hotel": 2.20,
    "5-Star Luxury Resort": 4.80,
}

FOOD_TIER_MULTIPLIERS = {
    "Street Food & Local Dhabas": 0.50,
    "Casual Dining & Cafes": 1.00,
    "Fine Dining & Multi-Cuisine": 2.70,
}

LOCAL_TRANSIT_MULTIPLIERS = {
    "Walking & Public Transit": 0.50,
    "Auto Rickshaw / Taxi / Rideshare": 1.00,
    "Chauffeured Private Car": 3.00,
}


class BudgetCalculator:
    """Calculates granular travel expenditure and analyzes budget health."""

    def __init__(self):
        pass

    def calculate_trip_budget(self, req: BudgetRequestSchema) -> Dict[str, Any]:
        """Compute comprehensive itemized budget using destination-specific rates and route logistics."""
        dest = get_destination_by_id(req.destination_id)
        if not dest:
            raise ValueError(f"Destination '{req.destination_id}' not found.")

        is_domestic = dest.get("is_domestic", True)
        scope_key = "Domestic" if is_domestic else "International"
        currency = dest.get("currency", "INR")
        dest_price_status = dest.get("price_status", "Estimated")

        # Traveler counts: adults and children
        num_travelers = max(1, req.num_travelers)
        num_children = max(0, req.num_children or 0)
        if req.num_adults is not None:
            num_adults = max(1, req.num_adults)
            num_travelers = num_adults + num_children
        else:
            num_adults = max(1, num_travelers - num_children)

        num_days = max(1, req.num_days)
        # For day trips (1 day), nights = 0. For multi-day, nights = num_days - 1
        num_nights = max(0, num_days - 1)

        # -------------------------------------------------------------
        # 1 & 2. Outbound and Return Transportation (Route-Aware)
        # -------------------------------------------------------------
        route_logistics = calculate_journey_logistics(
            origin_city=req.starting_location,
            destination_id=req.destination_id,
            transport_mode=req.transport_mode,
            num_travelers=num_travelers,
            personal_vehicle_mileage=req.personal_vehicle_mileage_kmpl or 15.0,
            fuel_price_inr=req.personal_vehicle_fuel_price_inr or 95.0
        )

        outbound_transport = route_logistics["outbound_cost_inr"]
        return_transport = route_logistics["return_cost_inr"]
        total_transportation = outbound_transport + return_transport

        # -------------------------------------------------------------
        # 3. Accommodation (Destination-Specific)
        # -------------------------------------------------------------
        # Rooms allocated: 2 travelers per standard room
        rooms_needed = math.ceil(num_travelers / 2.0)
        base_dest_accom = float(dest.get("accommodation_budget_per_night", 2500.0))
        tier_accom_mult = ACCOMMODATION_TIER_MULTIPLIERS.get(req.accommodation_tier, 1.0)
        nightly_room_rate = round(base_dest_accom * tier_accom_mult, 2)
        total_accommodation = round(nightly_room_rate * rooms_needed * num_nights, 2)

        # -------------------------------------------------------------
        # 4. Food & Dining (Destination-Specific per person per day)
        # -------------------------------------------------------------
        base_dest_food = float(dest.get("food_budget_per_person_per_day", 800.0))
        tier_food_mult = FOOD_TIER_MULTIPLIERS.get(req.food_tier, 1.0)
        daily_food_rate = round(base_dest_food * tier_food_mult, 2)
        total_food = round(daily_food_rate * num_days * num_travelers, 2)

        # -------------------------------------------------------------
        # 5. Local Transportation (Destination-Specific intra-city transit)
        # -------------------------------------------------------------
        base_dest_transit = float(dest.get("local_transport_budget_per_day", 400.0))
        tier_transit_mult = LOCAL_TRANSIT_MULTIPLIERS.get(req.local_transport_tier, 1.0)
        daily_local_transit = round(base_dest_transit * tier_transit_mult, 2)
        total_local_transport = round(daily_local_transit * num_days, 2)

        # -------------------------------------------------------------
        # 6. Attractions & Sightseeing (Adults & Children Data-Driven)
        # -------------------------------------------------------------
        attractions = get_attractions_for_destination(req.destination_id)
        if req.activities_level == "Free & Self-Guided":
            total_attractions = 0.0
            total_activities = round(100.0 * num_days * num_travelers, 2)
        elif req.activities_level == "Moderate Sightseeing":
            # Sum actual ticket admissions for top attractions up to duration quota
            quota = min(len(attractions), max(2, num_days * 2))
            top_sights = attractions[:quota]
            if top_sights:
                ticket_sum = sum(
                    (float(a.get("adult_ticket_price", a.get("estimated_ticket_inr", 50.0))) * num_adults)
                    + (float(a.get("child_ticket_price", 0.0)) * num_children)
                    for a in top_sights
                )
                total_attractions = round(ticket_sum, 2)
            else:
                base_sight = float(dest.get("sightseeing_budget_per_person_per_day", 400.0))
                total_attractions = round(base_sight * num_days * num_travelers, 2)
            total_activities = 0.0
        else:  # "All-Inclusive & Adventure Sports"
            quota = min(len(attractions), max(2, num_days * 2))
            top_sights = attractions[:quota]
            ticket_sum = sum(
                (float(a.get("adult_ticket_price", a.get("estimated_ticket_inr", 50.0))) * num_adults)
                + (float(a.get("child_ticket_price", 0.0)) * num_children)
                for a in top_sights
            ) if top_sights else 0.0
            # Adventure excursion allowance (guided safaris, scuba, sports)
            adventure_rate = 1400.0 if is_domestic else 4500.0
            total_attractions = round(ticket_sum, 2)
            total_activities = round(adventure_rate * num_days * num_travelers, 2)

        total_sightseeing = total_attractions + total_activities

        # -------------------------------------------------------------
        # 7. Miscellaneous & Shopping (Destination & Scope Aware)
        # -------------------------------------------------------------
        misc_rate = 400.0 if is_domestic else 1400.0
        total_miscellaneous = round(misc_rate * num_days * num_travelers, 2)

        # Subtotal before contingency
        subtotal = (
            total_transportation
            + total_accommodation
            + total_food
            + total_local_transport
            + total_sightseeing
            + total_miscellaneous
        )

        # -------------------------------------------------------------
        # 8. Contingency Allowance
        # -------------------------------------------------------------
        contingency_percent = max(0.0, min(50.0, req.contingency_percent))
        total_contingency = round(subtotal * (contingency_percent / 100.0), 2)

        # -------------------------------------------------------------
        # 9. Total Estimated Trip Cost & 10. Per Traveler Cost
        # -------------------------------------------------------------
        total_cost = round(subtotal + total_contingency, 2)
        per_person_cost = round(total_cost / num_travelers, 2)

        # Shortfall & Feasibility Analysis
        shortfall_info = self._analyze_budget_feasibility(
            total_cost=total_cost,
            target_budget=req.user_target_budget,
            category_totals={
                "Transportation": total_transportation,
                "Accommodation": total_accommodation,
                "Food & Dining": total_food,
                "Local Transport": total_local_transport,
                "Sightseeing & Activities": total_sightseeing,
                "Miscellaneous & Shopping": total_miscellaneous,
                "Contingency": total_contingency,
            },
            num_days=num_days,
            num_travelers=num_travelers,
            destination_name=dest["destination_name"]
        )

        assumptions_list = [
            f"Origin Route: {req.starting_location} to {dest['destination_name']} ({route_logistics['travel_distance_km']:,.0f} km one-way). {route_logistics['assumptions']}",
            f"Accommodation: {rooms_needed} room(s) for {num_nights} night(s) in {dest['destination_name']} @ INR {nightly_room_rate:,.0f}/room/night ({req.accommodation_tier}).",
            f"Food & Dining: Calculated for {num_travelers} traveler(s) over {num_days} day(s) @ INR {daily_food_rate:,.0f}/person/day ({req.food_tier}).",
            f"Local Transportation: {dest['destination_name']} intra-city transit @ INR {daily_local_transit:,.0f}/day ({req.local_transport_tier}).",
            f"Sightseeing & Tickets: {num_adults} adult(s) + {num_children} child(ren) admissions for {req.activities_level}.",
            f"Contingency Reserve: {contingency_percent}% buffer allocated on base expenses.",
            "All pricing estimates are data-driven. Live flight/hotel tariffs may fluctuate based on season."
        ]

        if "overland_warning" in route_logistics:
            assumptions_list.insert(0, f"⚠️ Note: {route_logistics['overland_warning']}")

        return {
            "destination_id": req.destination_id,
            "destination_name": dest["destination_name"],
            "country": dest["country"],
            "currency": currency,
            "price_status": dest_price_status,
            "origin_city": req.starting_location,
            "scope": scope_key,
            "num_travelers": num_travelers,
            "num_adults": num_adults,
            "num_children": num_children,
            "num_days": num_days,
            "num_nights": num_nights,
            "rooms_count": rooms_needed,
            "breakdown": {
                "Outbound Travel": round(outbound_transport, 2),
                "Return Travel": round(return_transport, 2),
                "Total Transportation": round(total_transportation, 2),
                "Accommodation": round(total_accommodation, 2),
                "Food & Dining": round(total_food, 2),
                "Local Transportation": round(total_local_transport, 2),
                "Attractions & Sightseeing": round(total_sightseeing, 2),
                "Miscellaneous & Shopping": round(total_miscellaneous, 2),
                "Contingency Reserve": round(total_contingency, 2),
            },
            "subtotal_inr": round(subtotal, 2),
            "contingency_percent": contingency_percent,
            "total_estimated_cost_inr": round(total_cost, 2),
            "per_person_cost_inr": round(per_person_cost, 2),
            "target_budget_inr": req.user_target_budget,
            "route_logistics": route_logistics,
            "shortfall_analysis": shortfall_info,
            "assumptions": assumptions_list
        }

    def _analyze_budget_feasibility(
        self,
        total_cost: float,
        target_budget: Optional[float],
        category_totals: Dict[str, float],
        num_days: int,
        num_travelers: int,
        destination_name: str = ""
    ) -> Dict[str, Any]:
        """Assess whether target budget is sufficient and offer actionable savings."""
        if not target_budget or target_budget <= 0:
            return {
                "status": "No Target Set",
                "is_sufficient": True,
                "difference_inr": 0.0,
                "suggestions": []
            }

        diff = target_budget - total_cost
        if diff >= 0:
            surplus_percent = (diff / target_budget) * 100.0
            return {
                "status": "Healthy Budget",
                "is_sufficient": True,
                "difference_inr": round(diff, 2),
                "surplus_percentage": round(surplus_percent, 1),
                "message": f"Your target budget of INR {target_budget:,.0f} comfortably covers the estimated trip expense of INR {total_cost:,.0f} with an INR {diff:,.0f} ({surplus_percent:.1f}%) surplus buffer.",
                "suggestions": [
                    "Your budget has healthy room for upgraded boutique lodging or specialty local experiences.",
                    "Allocate spare funds toward guided excursions or fine dining."
                ]
            }
        else:
            shortfall = abs(diff)
            shortfall_percent = (shortfall / target_budget) * 100.0
            sorted_drivers = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            top_drivers = [f"{k} (INR {v:,.0f})" for k, v in sorted_drivers[:2]]

            suggestions = []
            if sorted_drivers[0][0] == "Accommodation":
                suggestions.append("Switch from current lodging tier to a Budget Hotel or Guesthouse to save 35–40% on hotel nights.")
            elif sorted_drivers[0][0] == "Transportation":
                suggestions.append("Consider opting for AC Express Train or Sleeper Bus instead of Flight to reduce transit costs.")

            if num_days > 2:
                reduced_days = num_days - 1
                est_day_saving = (category_totals["Accommodation"] / max(1, num_days - 1)) + (category_totals["Food & Dining"] / num_days)
                suggestions.append(f"Shortening trip from {num_days} to {reduced_days} days saves approximately INR {est_day_saving:,.0f}.")

            suggestions.append("Opt for Free & Self-Guided walking tours for monuments instead of paid private excursion passes.")
            suggestions.append("Book tickets and intercity transport 3-4 weeks in advance to capture early-bird tariffs.")

            return {
                "status": "Budget Shortfall",
                "is_sufficient": False,
                "difference_inr": round(diff, 2),
                "shortfall_amount_inr": round(shortfall, 2),
                "shortfall_percentage": round(shortfall_percent, 1),
                "top_cost_drivers": top_drivers,
                "message": f"Estimated expenses (INR {total_cost:,.0f}) exceed your target budget of INR {target_budget:,.0f} by INR {shortfall:,.0f} ({shortfall_percent:.1f}% over budget).",
                "suggestions": suggestions
            }
