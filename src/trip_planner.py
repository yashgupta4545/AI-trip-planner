"""AI Trip Planner and Itinerary Generator for TripGenie AI.
Generates realistic, day-by-day itineraries adapted to duration, travel pace,
interests, travel group, and budget style using verified local attractions.
Includes complete journey logistics: outbound travel, arrival check-in,
local intra-city travel, hotel check-out, and return journey.
"""

from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

from src.data_loader import get_attractions_for_destination, get_destination_by_id
from src.route_service import calculate_journey_logistics


class TripPlanner:
    """Generates structured day-by-day travel schedules with complete journey planning."""

    def __init__(self):
        pass

    def generate_itinerary(
        self,
        destination_id: str,
        start_date: date,
        duration_days: int,
        travelers_count: int = 1,
        num_adults: Optional[int] = None,
        num_children: Optional[int] = 0,
        pace: str = "Balanced",
        travel_style: str = "Moderate",
        travel_group: str = "Solo",
        interests: Optional[List[str]] = None,
        origin_city: str = "Delhi",
        transport_mode: str = "Flight",
        total_budget: Optional[float] = None,
        accommodation_tier: str = "Mid-range 3-Star Hotel",
        food_tier: str = "Casual Dining & Cafes"
    ) -> Dict[str, Any]:
        """Create a full, personalized day-by-day itinerary including origin-to-destination transit."""
        dest = get_destination_by_id(destination_id)
        if not dest:
            raise ValueError(f"Destination with ID '{destination_id}' not found.")

        if duration_days < 1:
            raise ValueError("Trip duration must be at least 1 day.")

        # Traveler counts
        num_children = max(0, num_children or 0)
        if num_adults is not None:
            num_adults = max(1, num_adults)
            travelers_count = num_adults + num_children
        else:
            num_adults = max(1, travelers_count - num_children)

        # Calculate complete journey logistics from starting location
        route_info = calculate_journey_logistics(
            origin_city=origin_city,
            destination_id=destination_id,
            transport_mode=transport_mode,
            num_travelers=travelers_count
        )

        attractions = get_attractions_for_destination(destination_id)
        # Sort attractions prioritizing matched interests if provided
        if interests:
            matched = []
            others = []
            for a in attractions:
                cat_text = a.get("category", "")
                name_text = a.get("attraction_name", "")
                if any(i.lower() in cat_text.lower() or i.lower() in name_text.lower() for i in interests):
                    matched.append(a)
                else:
                    others.append(a)
            available_attractions = matched + others
        else:
            available_attractions = list(attractions)

        days_schedule = []
        attraction_cursor = 0
        total_activity_costs = 0.0
        daily_local_transit_inr = float(dest.get("local_transport_budget_per_day", 400.0))

        for day_num in range(1, duration_days + 1):
            current_date = start_date + timedelta(days=day_num - 1)
            day_schedule = self._build_day_plan(
                day_num=day_num,
                total_days=duration_days,
                current_date=current_date,
                dest=dest,
                origin_city=origin_city,
                route_info=route_info,
                available_attractions=available_attractions,
                attraction_cursor=attraction_cursor,
                pace=pace,
                travel_style=travel_style,
                travel_group=travel_group,
                travelers_count=travelers_count,
                num_adults=num_adults,
                num_children=num_children,
                accommodation_tier=accommodation_tier,
                food_tier=food_tier,
                daily_local_transit_inr=daily_local_transit_inr
            )
            attraction_cursor += day_schedule["attractions_used_count"]
            total_activity_costs += day_schedule["day_ticket_cost_total"]
            days_schedule.append(day_schedule)

        end_date = start_date + timedelta(days=duration_days - 1)

        return {
            "destination_id": destination_id,
            "destination_name": dest["destination_name"],
            "country": dest["country"],
            "region": dest["region"],
            "origin_city": origin_city,
            "transport_mode": route_info["transport_mode"],
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "duration_days": duration_days,
            "travelers_count": travelers_count,
            "num_adults": num_adults,
            "num_children": num_children,
            "pace": pace,
            "travel_style": travel_style,
            "travel_group": travel_group,
            "total_budget": total_budget,
            "accommodation_tier": accommodation_tier,
            "food_tier": food_tier,
            "route_logistics": route_info,
            "booking_search_links": route_info.get("search_links", {}),
            "outbound_transport_cost_inr": route_info["outbound_cost_inr"],
            "return_transport_cost_inr": route_info["return_cost_inr"],
            "total_activity_cost_inr": round(total_activity_costs, 2),
            "days": days_schedule,
            "transport_notes": dest.get("transport_notes", "Accessible via flight, rail, and road networks."),
            "climate_summary": dest.get("climate_summary", "Pleasant seasonal conditions."),
            "generated_at": datetime.now().isoformat()
        }

    def _build_day_plan(
        self,
        day_num: int,
        total_days: int,
        current_date: date,
        dest: Dict[str, Any],
        origin_city: str,
        route_info: Dict[str, Any],
        available_attractions: List[Dict],
        attraction_cursor: int,
        pace: str,
        travel_style: str,
        travel_group: str,
        travelers_count: int,
        num_adults: int,
        num_children: int,
        accommodation_tier: str,
        food_tier: str,
        daily_local_transit_inr: float
    ) -> Dict[str, Any]:
        """Construct a balanced single-day plan with morning, afternoon, and evening slots."""
        dest_name = dest["destination_name"]
        activities = []
        day_ticket_total = 0.0
        used_count = 0

        # DAY 1: Outbound Journey & Arrival Check-in
        if day_num == 1:
            day_theme = "Outbound Journey, Arrival & City Orientation"
            transit_mode = route_info.get("transport_mode", "Flight")
            outbound_dur = route_info.get("outbound_duration_hours", 2.5)
            is_same_city = route_info.get("is_same_city", False)

            if is_same_city:
                m_title = f"Local Rendezvous & Intra-City Departure in {origin_city}"
                m_desc = f"Depart from home base in {origin_city} via local transit to begin your {dest_name} staycation."
                tip_text = "Pack light daypacks and have local transit cards/passes handy."
            else:
                m_title = f"Outbound Journey: {origin_city} to {dest_name} ({transit_mode})"
                m_desc = (
                    f"Board your {transit_mode.lower()} from {origin_city} to {dest_name} "
                    f"(approx. {outbound_dur} hrs travel time, {route_info.get('travel_distance_km', 0):,.0f} km route). "
                    f"Arrive at destination terminal and transfer to {accommodation_tier} for check-in and unpacking."
                )
                tip_text = "Keep government photo IDs and transport booking confirmations accessible."

            activities.append({
                "slot": "Morning",
                "time": "08:30 AM - 12:30 PM",
                "title": m_title,
                "description": m_desc,
                "duration_hours": outbound_dur,
                "ticket_cost_inr": 0.0,  # Intercity transport accounted in centralized transportation category
                "recommendation_tip": tip_text
            })

            # Welcome Lunch
            activities.append({
                "slot": "Midday Break",
                "time": "12:30 PM - 02:00 PM",
                "title": f"Welcome Lunch & Rest in {dest_name}",
                "description": f"Enjoy a refreshing lunch sampling regional specialties ({food_tier}). Freshen up at your hotel.",
                "duration_hours": 1.5,
                "ticket_cost_inr": 0.0,
                "recommendation_tip": "Hydrate well and ask the hotel concierge for the day's local map."
            })

            # Afternoon Sights
            attr_a = None
            if attraction_cursor + used_count < len(available_attractions):
                attr_a = available_attractions[attraction_cursor + used_count]
                used_count += 1
                a_title = attr_a["attraction_name"]
                a_desc = attr_a["description"]
                ad_p = float(attr_a.get("adult_ticket_price", attr_a.get("estimated_ticket_inr", 50.0)))
                ch_p = float(attr_a.get("child_ticket_price", 0.0))
                a_cost = (ad_p * num_adults) + (ch_p * num_children)
                a_dur = float(attr_a.get("typical_duration_hours", 2.0))
            else:
                a_title = f"{dest_name} Old Town & Heritage Walk"
                a_desc = f"Gentle orientation walk exploring iconic lanes, landmark facades, and photography spots in {dest_name}."
                a_cost = 0.0
                a_dur = 2.0

            day_ticket_total += a_cost
            activities.append({
                "slot": "Afternoon",
                "time": "02:30 PM - 05:30 PM",
                "title": a_title,
                "description": a_desc,
                "duration_hours": a_dur,
                "ticket_cost_inr": a_cost,
                "recommendation_tip": "Ideal leisurely start without strenuous physical exertion after transit."
            })

            # Evening Sunset & Promenade
            activities.append({
                "slot": "Evening",
                "time": "06:00 PM - 09:00 PM",
                "title": f"Sunset Promenade & Evening Welcome Dinner",
                "description": f"Stroll through bustling local markets, take in the evening skyline, and enjoy authentic dinner.",
                "duration_hours": 2.5,
                "ticket_cost_inr": 0.0,
                "recommendation_tip": "Get a good night's rest to prepare for tomorrow's exploration."
            })

        # FINAL DAY: Sights, Check-out & Return Journey
        elif day_num == total_days and total_days > 1:
            day_theme = "Morning Sights, Hotel Check-out & Return Journey"
            transit_mode = route_info.get("transport_mode", "Flight")
            ret_dur = route_info.get("return_duration_hours", 2.5)

            # Morning Sight
            attr_m = None
            if attraction_cursor + used_count < len(available_attractions):
                attr_m = available_attractions[attraction_cursor + used_count]
                used_count += 1
                m_title = attr_m["attraction_name"]
                m_desc = attr_m["description"]
                ad_p = float(attr_m.get("adult_ticket_price", attr_m.get("estimated_ticket_inr", 50.0)))
                ch_p = float(attr_m.get("child_ticket_price", 0.0))
                m_cost = (ad_p * num_adults) + (ch_p * num_children)
                m_dur = float(attr_m.get("typical_duration_hours", 2.0))
            else:
                m_title = f"{dest_name} Artisan Markets & Souvenir Discovery"
                m_desc = f"Pick up handicrafts, regional delicacies, and souvenirs before departure."
                m_cost = 0.0
                m_dur = 2.0

            day_ticket_total += m_cost
            activities.append({
                "slot": "Morning",
                "time": "09:00 AM - 11:30 AM",
                "title": m_title,
                "description": m_desc,
                "duration_hours": m_dur,
                "ticket_cost_inr": m_cost,
                "recommendation_tip": "Carry cash/UPI for local artisan bazaars and pack breakables securely."
            })

            # Midday Check-out & Farewell Lunch
            activities.append({
                "slot": "Midday Break",
                "time": "11:30 AM - 01:30 PM",
                "title": f"Hotel Check-out & Farewell Regional Lunch",
                "description": f"Complete check-out formalities at your accommodation. Savor a final traditional lunch in {dest_name}.",
                "duration_hours": 2.0,
                "ticket_cost_inr": 0.0,
                "recommendation_tip": "Double-check room for chargers, documents, and baggage tags."
            })

            # Afternoon Return Journey
            activities.append({
                "slot": "Afternoon",
                "time": "02:00 PM - 06:30 PM",
                "title": f"Return Journey: {dest_name} to {origin_city} ({transit_mode})",
                "description": (
                    f"Board your return {transit_mode.lower()} back to {origin_city} "
                    f"(approx. {ret_dur} hrs travel time). Arrive at home terminal with unforgettable memories."
                ),
                "duration_hours": ret_dur,
                "ticket_cost_inr": 0.0,  # Accounted in centralized return travel category
                "recommendation_tip": "Arrive at terminal 90-120 mins before departure for flight check-in or boarding."
            })

        # MIDDLE DAYS (or Day 1 of 1-day trip)
        else:
            if pace == "Relaxed":
                day_theme = "Scenic Exploration & Cultural Charm"
            elif pace == "Packed":
                day_theme = "Action-Packed Sightseeing Highlights"
            else:
                day_theme = "Heritage, Natural Wonders & Local Discovery"

            # Morning slot
            attr_m = None
            if attraction_cursor + used_count < len(available_attractions):
                attr_m = available_attractions[attraction_cursor + used_count]
                used_count += 1
                m_title = attr_m["attraction_name"]
                m_desc = attr_m["description"]
                ad_p = float(attr_m.get("adult_ticket_price", attr_m.get("estimated_ticket_inr", 50.0)))
                ch_p = float(attr_m.get("child_ticket_price", 0.0))
                m_cost = (ad_p * num_adults) + (ch_p * num_children)
                m_dur = float(attr_m.get("typical_duration_hours", 2.0))
            else:
                m_title = f"{dest_name} Scenic Viewpoint & Heritage Tour"
                m_desc = f"Explore scenic viewpoints and historic architecture across {dest_name}."
                m_cost = 0.0
                m_dur = 2.0

            day_ticket_total += m_cost
            activities.append({
                "slot": "Morning",
                "time": "09:00 AM - 12:30 PM",
                "title": m_title,
                "description": m_desc,
                "duration_hours": m_dur,
                "ticket_cost_inr": m_cost,
                "recommendation_tip": "Start early to capture morning golden hour photography."
            })

            # Midday Lunch
            activities.append({
                "slot": "Midday Break",
                "time": "12:30 PM - 02:00 PM",
                "title": f"Regional Culinary Lunch in {dest_name}",
                "description": f"Savor authentic regional dishes ({food_tier}). Take a comfortable midday break.",
                "duration_hours": 1.5,
                "ticket_cost_inr": 0.0,
                "recommendation_tip": "Recharge batteries and rest during the hottest midday hours."
            })

            # Afternoon slot
            attr_a = None
            if attraction_cursor + used_count < len(available_attractions):
                attr_a = available_attractions[attraction_cursor + used_count]
                used_count += 1
                a_title = attr_a["attraction_name"]
                a_desc = attr_a["description"]
                ad_p = float(attr_a.get("adult_ticket_price", attr_a.get("estimated_ticket_inr", 50.0)))
                ch_p = float(attr_a.get("child_ticket_price", 0.0))
                a_cost = (ad_p * num_adults) + (ch_p * num_children)
                a_dur = float(attr_a.get("typical_duration_hours", 2.0))
            else:
                a_title = f"{dest_name} Cultural Centre & Botanical Gardens"
                a_desc = f"Explore lush botanical parks and cultural heritage exhibits."
                a_cost = 50.0 * travelers_count
                a_dur = 2.0

            day_ticket_total += a_cost
            activities.append({
                "slot": "Afternoon",
                "time": "02:00 PM - 05:30 PM",
                "title": a_title,
                "description": a_desc,
                "duration_hours": a_dur,
                "ticket_cost_inr": a_cost,
                "recommendation_tip": "Great time for guided exhibits and quiet discovery."
            })

            # Evening slot
            if pace != "Relaxed":
                attr_e = None
                if attraction_cursor + used_count < len(available_attractions) and pace == "Packed":
                    attr_e = available_attractions[attraction_cursor + used_count]
                    used_count += 1
                    e_title = attr_e["attraction_name"]
                    e_desc = attr_e["description"]
                    ad_p = float(attr_e.get("adult_ticket_price", attr_e.get("estimated_ticket_inr", 50.0)))
                    ch_p = float(attr_e.get("child_ticket_price", 0.0))
                    e_cost = (ad_p * num_adults) + (ch_p * num_children)
                    e_dur = float(attr_e.get("typical_duration_hours", 2.0))
                else:
                    e_title = f"Night Bazaars & Cultural Entertainment of {dest_name}"
                    e_desc = f"Soak in the night atmosphere, visit craft markets, and enjoy street performances."
                    e_cost = 0.0
                    e_dur = 2.5

                day_ticket_total += e_cost
                activities.append({
                    "slot": "Evening",
                    "time": "06:00 PM - 09:30 PM",
                    "title": e_title,
                    "description": e_desc,
                    "duration_hours": e_dur,
                    "ticket_cost_inr": e_cost,
                    "recommendation_tip": "Sample regional street delicacies and sunset vistas."
                })

        return {
            "day_number": day_num,
            "date": current_date.strftime("%A, %b %d, %Y"),
            "theme": day_theme,
            "activities": activities,
            "day_ticket_cost_total": round(day_ticket_total, 2),
            "estimated_local_transit_inr": round(daily_local_transit_inr, 2),
            "attractions_used_count": used_count
        }
