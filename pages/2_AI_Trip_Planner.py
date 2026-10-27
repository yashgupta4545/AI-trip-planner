"""AI Trip Planner & Itinerary Generator - Complete Origin-to-Destination Journey Scheduling."""

from datetime import date, timedelta
import streamlit as st
from streamlit_folium import st_folium

from src.config import (
    APP_NAME, ACCOMMODATION_TIERS, TRANSPORT_MODES
)
from src.data_loader import get_all_destinations, get_destination_by_id, get_distinct_interests
from src.data_validation import RecommendationQuerySchema
from src.export_service import export_itinerary_to_csv, export_trip_to_json, export_trip_to_pdf
from src.llm_service import generate_itinerary_narrative
from src.map_service import create_destination_map
from src.recommendation_engine import get_recommendation_engine
from src.trip_planner import TripPlanner
from src.trip_storage import save_trip
from src.style_service import apply_custom_theme, render_sidebar_brand

st.set_page_config(
    page_title=f"AI Trip Planner — {APP_NAME}",
    page_icon="✨",
    layout="wide"
)

apply_custom_theme()
render_sidebar_brand()

st.title("✨ AI Trip Planner & Journey Generator")
st.markdown("Plan your complete journey from your starting city to destination and back with day-by-day scheduling.")

# Initialize Trip Planner & Engine
planner = TripPlanner()
recommender = get_recommendation_engine()
all_dests_df = get_all_destinations()

# Check incoming session state from Explore Destinations or My Trips
incoming_dest_id = st.session_state.get("selected_dest_id", None)
incoming_origin = st.session_state.get("planner_origin_city", "Delhi")
incoming_days = int(st.session_state.get("planner_days", 3))
incoming_travelers = int(st.session_state.get("planner_travelers", 2))
incoming_budget = st.session_state.get("planner_budget", None)

dest_options = {
    f"{r['destination_name']} ({r['country']})": r["destination_id"]
    for _, r in all_dests_df.iterrows()
}

# -------------------------------------------------------------
# Section 1: AI Recommendation Assistant (Optional)
# -------------------------------------------------------------
with st.expander("✨ Need Suggestions? Get AI Destination Recommendations", expanded=incoming_dest_id is None):
    st.markdown("Specify your starting city and travel preferences to receive data-driven destination matches.")
    c_orig, c_scope, c_dur, c_bud = st.columns(4)
    with c_orig:
        rec_origin = st.text_input("Origin City", value=incoming_origin, key="rec_ai_origin")
    with c_scope:
        rec_scope = st.selectbox("Travel Scope", ["Domestic", "International", "All"], index=0, key="rec_ai_scope")
    with c_dur:
        rec_dur_days = st.number_input("Target Duration (Days)", min_value=1, max_value=30, value=incoming_days, key="rec_ai_dur")
    with c_bud:
        rec_max_bud = st.number_input("Max Daily Budget (INR)", min_value=1000.0, max_value=30000.0, value=4000.0, step=500.0, key="rec_ai_bud")

    all_ints = get_distinct_interests()
    safe_defaults = [i for i in ["Palaces", "Heritage & Culture", "Beach", "Mountains", "History"] if i in all_ints]
    if not safe_defaults and len(all_ints) >= 2:
        safe_defaults = all_ints[:2]
    rec_ints = st.multiselect("Your Travel Interests", all_ints, default=safe_defaults, key="rec_ai_ints")
    rec_group = st.selectbox("Travel Group", ["Solo", "Couple", "Family", "Friends / Group"], key="rec_ai_grp")

    if st.button("Find Matching Destinations", type="primary", key="btn_find_matching"):
        q_schema = RecommendationQuerySchema(
            origin_city=rec_origin,
            travel_scope=rec_scope,
            selected_interests=rec_ints,
            travel_group=rec_group,
            max_budget_inr=rec_max_bud,
            trip_duration_days=rec_dur_days
        )
        recs, notice = recommender.recommend(q_schema, top_n=3)
        if notice:
            st.info(notice)
        
        st.markdown("#### Top Ranked Destinations For You:")
        cols_rec = st.columns(len(recs))
        for idx, r in enumerate(recs):
            with cols_rec[idx]:
                with st.container(border=True):
                    st.markdown(f"**{r['destination_name']}** ({r['country']})")
                    st.metric("Match Score", f"{r['match_score']}%")
                    st.caption(r['explanation'])
                    st.markdown(f"**Daily Est:** INR {r['estimated_daily_budget_inr']:,.0f}")
                    if st.button("Select This Destination", key=f"sel_rec_{r['destination_id']}", use_container_width=True):
                        st.session_state["selected_dest_id"] = r["destination_id"]
                        st.session_state["planner_origin_city"] = rec_origin
                        st.session_state["planner_days"] = rec_dur_days
                        st.rerun()

st.divider()

# -------------------------------------------------------------
# Section 2: Complete Journey Travel Parameters Form
# -------------------------------------------------------------
st.subheader("1. Complete Journey Parameters")

# Locate current index for dropdown
options_list = list(dest_options.keys())
default_index = 0
if incoming_dest_id:
    for idx, (label, d_id) in enumerate(dest_options.items()):
        if d_id == incoming_dest_id:
            default_index = idx
            break

r1_c1, r1_c2, r1_c3, r1_c4 = st.columns([1.5, 1.2, 1, 1])
with r1_c1:
    selected_label = st.selectbox("Destination", options_list, index=default_index)
    chosen_dest_id = dest_options[selected_label]
with r1_c2:
    start_city = st.text_input("Starting City / Origin", value=incoming_origin)
with r1_c3:
    start_dt = st.date_input("Departure Date", value=date.today() + timedelta(days=7), min_value=date.today())
with r1_c4:
    trip_days = st.number_input("Duration (Days)", min_value=1, max_value=30, value=incoming_days, step=1)

return_dt = start_dt + timedelta(days=trip_days - 1)

r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
with r2_c1:
    num_adults = st.number_input("Adults", min_value=1, max_value=20, value=max(1, incoming_travelers), step=1)
with r2_c2:
    num_children = st.number_input("Children", min_value=0, max_value=15, value=0, step=1)
with r2_c3:
    transport_pref = st.selectbox(
        "Intercity Transport Mode",
        TRANSPORT_MODES,
        index=0 if "Flight" in TRANSPORT_MODES else 0
    )
with r2_c4:
    target_budget = st.number_input(
        "Total Budget (INR, Optional)",
        min_value=0.0,
        max_value=2000000.0,
        value=float(incoming_budget) if incoming_budget else 0.0,
        step=5000.0
    )

r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
with r3_c1:
    accom_category = st.selectbox("Accommodation Tier", ACCOMMODATION_TIERS, index=2)
with r3_c2:
    food_pref = st.selectbox(
        "Food Preference",
        ["Casual Dining & Cafes", "Street Food & Local Dhabas", "Fine Dining & Multi-Cuisine"],
        index=0
    )
with r3_c3:
    trip_pace = st.selectbox("Travel Pace", ["Balanced", "Relaxed", "Packed"], index=0)
with r3_c4:
    group_type = st.selectbox("Travel Group", ["Couple", "Solo", "Family", "Friends / Group"], index=0)

all_ints = get_distinct_interests()
selected_interests = st.multiselect("Specific Travel Interests (Optional)", all_ints, default=[])

dest_details = get_destination_by_id(chosen_dest_id)
tot_travelers = num_adults + num_children

st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
generate_clicked = st.button("⚡ Generate Complete Journey & Itinerary", type="primary", use_container_width=True)

# Generate or Retrieve Itinerary from Session State
should_regenerate = (
    generate_clicked
    or "current_itinerary" not in st.session_state
    or st.session_state.get("itinerary_dest_id") != chosen_dest_id
    or st.session_state.get("itinerary_origin") != start_city
    or st.session_state.get("itinerary_days") != trip_days
)

if should_regenerate:
    with st.spinner("Generating journey logistics, scheduling attractions, and calculating arrival/departure routes..."):
        itinerary = planner.generate_itinerary(
            destination_id=chosen_dest_id,
            start_date=start_dt,
            duration_days=trip_days,
            travelers_count=tot_travelers,
            num_adults=num_adults,
            num_children=num_children,
            pace=trip_pace,
            travel_style=accom_category.split()[0],
            travel_group=group_type,
            interests=selected_interests if selected_interests else None,
            origin_city=start_city,
            transport_mode=transport_pref,
            total_budget=target_budget if target_budget > 0 else None,
            accommodation_tier=accom_category,
            food_tier=food_pref
        )
        st.session_state["current_itinerary"] = itinerary
        st.session_state["itinerary_dest_id"] = chosen_dest_id
        st.session_state["itinerary_origin"] = start_city
        st.session_state["itinerary_days"] = trip_days
else:
    itinerary = st.session_state["current_itinerary"]

# -------------------------------------------------------------
# Section 3: Journey Logistics & Booking Search
# -------------------------------------------------------------
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.subheader(f"2. Journey Plan: {itinerary['origin_city']} ⇄ {itinerary['destination_name']}")

# Route Logistics Card
route = itinerary.get("route_logistics", {})
with st.container(border=True):
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    with col_r1:
        st.metric("Travel Distance", f"{route.get('travel_distance_km', 0):,.0f} km")
        st.caption(f"Mode: **{route.get('transport_mode', transport_pref)}**")
    with col_r2:
        st.metric("Outbound Duration", f"{route.get('outbound_duration_hours', 2)} hrs")
        st.caption(f"Departure: **{itinerary['start_date']}**")
    with col_r3:
        st.metric("Return Duration", f"{route.get('return_duration_hours', 2)} hrs")
        st.caption(f"Return: **{itinerary['end_date']}**")
    with col_r4:
        tot_trans = itinerary.get("outbound_transport_cost_inr", 0) + itinerary.get("return_transport_cost_inr", 0)
        st.metric("Round-Trip Transit Cost", f"INR {tot_trans:,.0f}")
        st.caption(f"Price Status: `{route.get('price_status', 'Estimated')}`")

    st.info(f"ℹ️ **Route Assumptions:** {route.get('assumptions', 'Standard scheduled travel route.')}")

    # Real-Time Search Links
    search_links = itinerary.get("booking_search_links", {})
    if search_links:
        st.markdown("**External Search & Availability Links:**")
        lnk_cols = st.columns(min(4, len(search_links)))
        for i, (title, url) in enumerate(search_links.items()):
            with lnk_cols[i % len(lnk_cols)]:
                st.markdown(f"🔗 [{title}]({url})")

# -------------------------------------------------------------
# Section 4: Day-by-Day Timeline Display
# -------------------------------------------------------------
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.subheader(f"3. Day-by-Day Schedule ({itinerary['duration_days']} Days)")

# Narrative Banner
narrative_res = generate_itinerary_narrative(itinerary)
st.info(f"🧭 **Trip Narrative:** {narrative_res['narrative']}\n\n*Source: {narrative_res['provider']}*")

tab_schedule, tab_map, tab_actions = st.tabs(["📋 Day-by-Day Timeline", "📍 Geographic Map", "💾 Save & Export"])

with tab_schedule:
    for day in itinerary["days"]:
        with st.container(border=True):
            d_col1, d_col2 = st.columns([3, 1])
            with d_col1:
                st.markdown(f"### Day {day['day_number']} — {day['theme']}")
                st.caption(f"📅 {day['date']} • Local Transit Budget: `INR {day.get('estimated_local_transit_inr', 400):,.0f}`")
            with d_col2:
                st.markdown(
                    f"<div style='text-align: right; color: #0d9488; font-weight: bold;'>Est. Tickets: INR {day['day_ticket_cost_total']:,.0f}</div>",
                    unsafe_allow_html=True
                )
            
            st.divider()
            
            # Activities in this day
            for act in day["activities"]:
                slot_emoji = "🌅" if act["slot"] == "Morning" else ("🍽️" if act["slot"] == "Midday Break" else ("☀️" if act["slot"] == "Afternoon" else "🌆"))
                st.markdown(f"**{slot_emoji} {act['slot']} ({act['time']}): {act['title']}**")
                st.write(act["description"])
                st.caption(f"⏱️ Duration: {act['duration_hours']} hrs | 💡 Tip: {act['recommendation_tip']}")
                if act.get("ticket_cost_inr", 0) > 0:
                    st.caption(f"🎟️ Ticket: INR {act['ticket_cost_inr']:,.0f}")
                st.markdown("<div style='height: 6px;'></div>", unsafe_allow_html=True)

with tab_map:
    st.markdown("#### Destination & Sights Map")
    d_map = create_destination_map(chosen_dest_id)
    if d_map:
        st_folium(d_map, width=1200, height=500)
    else:
        st.warning("Map coordinates unavailable for this destination.")

with tab_actions:
    st.markdown("#### Save & Export Options")
    st.write("Persist this itinerary to your saved journeys or download in your preferred format.")
    
    col_save, col_pdf, col_csv, col_json = st.columns(4)
    
    with col_save:
        if st.button("💾 Save to 'My Trips'", use_container_width=True):
            trip_id = save_trip(
                destination_id=chosen_dest_id,
                destination_name=itinerary["destination_name"],
                start_date=itinerary["start_date"],
                duration_days=itinerary["duration_days"],
                travelers_count=itinerary["travelers_count"],
                itinerary_data=itinerary
            )
            st.success(f"Trip saved successfully! Reference ID: `{trip_id}`. View anytime in 'My Trips'.")
    
    with col_pdf:
        pdf_data = export_trip_to_pdf(itinerary)
        st.download_button(
            label="📄 Download PDF",
            data=pdf_data,
            file_name=f"TripGenie_{itinerary['destination_name']}_{itinerary['duration_days']}Days.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    with col_csv:
        csv_data = export_itinerary_to_csv(itinerary)
        st.download_button(
            label="📊 Download CSV",
            data=csv_data,
            file_name=f"TripGenie_{itinerary['destination_name']}_schedule.csv",
            mime="text/csv",
            use_container_width=True
        )
        
    with col_json:
        json_data = export_trip_to_json(itinerary)
        st.download_button(
            label="⚙️ Download JSON",
            data=json_data,
            file_name=f"TripGenie_{itinerary['destination_name']}_itinerary.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    if st.button("💰 Calculate Granular Budget Breakdown for This Journey", type="secondary"):
        st.session_state["budget_calc_dest_id"] = chosen_dest_id
        st.session_state["budget_calc_origin"] = start_city
        st.session_state["budget_calc_days"] = trip_days
        st.session_state["budget_calc_travelers"] = tot_travelers
        st.session_state["budget_calc_adults"] = num_adults
        st.session_state["budget_calc_children"] = num_children
        st.session_state["budget_calc_transport"] = transport_pref
        st.session_state["budget_calc_target"] = target_budget
        st.switch_page("pages/3_Budget_Calculator.py")
