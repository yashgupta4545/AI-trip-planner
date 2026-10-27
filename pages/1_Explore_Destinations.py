"""Explore Destinations - Interactive Catalog, Geospatial Map, Budget Discovery & Comparison Engine."""

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium

from src.config import APP_NAME, TRANSPORT_MODES
from src.data_loader import (
    get_all_destinations,
    get_attractions_for_destination,
    get_destination_by_id,
    get_distinct_countries,
    get_distinct_destination_types,
    get_distinct_interests,
    search_destinations
)
from src.map_service import create_multi_destination_map
from src.budget_calculator import BudgetCalculator
from src.data_validation import BudgetRequestSchema
from src.route_service import calculate_journey_logistics
from src.style_service import apply_custom_theme, render_sidebar_brand

st.set_page_config(
    page_title=f"Explore Destinations — {APP_NAME}",
    page_icon="🌍",
    layout="wide"
)

apply_custom_theme()
render_sidebar_brand()

st.title("🌍 Explore Destinations")
st.markdown(
    "Discover **320+ destinations** in India and around the globe with realistic, "
    "destination-specific pricing and origin-aware journey estimates."
)

# Shared centralized calculator instance
calc = BudgetCalculator()

# -------------------------------------------------------------
# Section C: Find Destinations Within Your Budget
# -------------------------------------------------------------
with st.expander("🎯 Find Destinations Within Your Budget", expanded=False):
    st.markdown("Specify your starting city and total available budget to find trips that fit comfortably.")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    with b_col1:
        rec_origin = st.text_input("Your Starting City", value="Delhi", key="budget_rec_origin")
    with b_col2:
        rec_budget = st.number_input("Your Total Budget (INR)", min_value=3000.0, max_value=2000000.0, value=25000.0, step=5000.0, key="budget_rec_amount")
    with b_col3:
        rec_travelers = st.number_input("Travelers", min_value=1, max_value=20, value=2, step=1, key="budget_rec_travelers")

    b_col4, b_col5, b_col6 = st.columns(3)
    with b_col4:
        rec_duration = st.number_input("Trip Duration (Days)", min_value=1, max_value=21, value=3, step=1, key="budget_rec_dur")
    with b_col5:
        rec_scope = st.selectbox("Scope", ["All", "Domestic", "International"], index=1, key="budget_rec_scope")
    with b_col6:
        all_ints = get_distinct_interests()
        rec_interests = st.multiselect("Preferred Interests", all_ints, default=[], key="budget_rec_interests")

    if st.button("🔍 Find Matching Trips Within Budget", type="primary"):
        all_df = get_all_destinations()
        if rec_scope == "Domestic":
            candidates_df = all_df[all_df["is_domestic"]]
        elif rec_scope == "International":
            candidates_df = all_df[~all_df["is_domestic"]]
        else:
            candidates_df = all_df

        candidate_results = []
        for _, r in candidates_df.iterrows():
            d_id = r["destination_id"]
            # Fast centralized estimation
            req = BudgetRequestSchema(
                destination_id=d_id,
                starting_location=rec_origin,
                num_travelers=rec_travelers,
                num_days=rec_duration,
                transport_mode="Train (Express / AC)" if r.get("is_domestic") else "Flight",
                accommodation_tier="Budget Hotel / Guesthouse" if r.get("budget_category") == "Budget" else "Mid-range 3-Star Hotel",
                food_tier="Casual Dining & Cafes",
                local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
                activities_level="Moderate Sightseeing",
                contingency_percent=10.0,
                user_target_budget=rec_budget
            )
            try:
                b_res = calc.calculate_trip_budget(req)
                tot_cost = b_res["total_estimated_cost_inr"]
                
                # Check interest overlap
                dest_ints = str(r.get("interests", "")).lower()
                int_matches = sum(1 for i in rec_interests if i.lower() in dest_ints) if rec_interests else 1

                candidate_results.append({
                    "destination_id": d_id,
                    "destination_name": r["destination_name"],
                    "country": r["country"],
                    "region": r["region"],
                    "total_cost": tot_cost,
                    "per_person": b_res["per_person_cost_inr"],
                    "transit_cost": b_res["breakdown"]["Total Transportation"],
                    "lodging_cost": b_res["breakdown"]["Accommodation"],
                    "price_status": r.get("price_status", "Estimated"),
                    "fits_budget": tot_cost <= rec_budget,
                    "diff": rec_budget - tot_cost,
                    "interest_matches": int_matches,
                    "recommended_duration": r["recommended_duration_days"]
                })
            except Exception:
                continue

        # Split fits vs over budget
        fitting_trips = [c for c in candidate_results if c["fits_budget"]]
        # Rank by: 1. Budget suitability (high surplus/usage), 2. interest matches, 3. transit affordability
        fitting_trips.sort(key=lambda x: (x["interest_matches"], -abs(x["diff"])), reverse=True)

        if fitting_trips:
            st.success(f"🎉 Found **{len(fitting_trips)}** destinations within your budget of INR {rec_budget:,.0f} from {rec_origin}!")
            rec_cols = st.columns(min(3, len(fitting_trips)))
            for idx, c in enumerate(fitting_trips[:6]):
                with rec_cols[idx % 3]:
                    with st.container(border=True):
                        st.markdown(f"**{c['destination_name']}** ({c['country']})")
                        st.caption(f"📍 {c['region']} • Price: `{c['price_status']}`")
                        st.metric("Total Trip Cost", f"INR {c['total_cost']:,.0f}", delta=f"INR {c['diff']:,.0f} surplus")
                        st.markdown(f"""
                        - **Round-Trip Transit:** INR {c['transit_cost']:,.0f}
                        - **Lodging ({rec_duration-1} nights):** INR {c['lodging_cost']:,.0f}
                        - **Per Traveler:** INR {c['per_person']:,.0f}
                        """)
                        if st.button("Plan This Trip", key=f"btn_rec_plan_{c['destination_id']}", use_container_width=True):
                            st.session_state["selected_dest_id"] = c["destination_id"]
                            st.session_state["planner_origin_city"] = rec_origin
                            st.session_state["planner_days"] = rec_duration
                            st.session_state["planner_travelers"] = rec_travelers
                            st.session_state["planner_budget"] = rec_budget
                            st.switch_page("pages/2_AI_Trip_Planner.py")
        else:
            # Show closest affordable alternatives
            candidate_results.sort(key=lambda x: x["total_cost"])
            st.warning(f"⚠️ No destinations strictly fit under INR {rec_budget:,.0f} for a {rec_duration}-day trip from {rec_origin}.")
            st.markdown("#### Closest Affordable Alternatives:")
            alt_cols = st.columns(min(3, len(candidate_results)))
            for idx, c in enumerate(candidate_results[:3]):
                shortfall = abs(c["diff"])
                with alt_cols[idx]:
                    with st.container(border=True):
                        st.markdown(f"**{c['destination_name']}** ({c['country']})")
                        st.metric("Estimated Cost", f"INR {c['total_cost']:,.0f}", delta=f"-INR {shortfall:,.0f} needed", delta_color="inverse")
                        st.info(f"Requires an additional **INR {shortfall:,.0f}** to cover estimated travel & lodging expenses.")
                        if st.button("Plan Trip Anyway", key=f"btn_rec_alt_{c['destination_id']}", use_container_width=True):
                            st.session_state["selected_dest_id"] = c["destination_id"]
                            st.session_state["planner_origin_city"] = rec_origin
                            st.session_state["planner_days"] = rec_duration
                            st.session_state["planner_travelers"] = rec_travelers
                            st.session_state["planner_budget"] = c["total_cost"]
                            st.switch_page("pages/2_AI_Trip_Planner.py")

st.divider()

# -------------------------------------------------------------
# Section A: Search and Filters
# -------------------------------------------------------------
st.subheader("Filter & Explore Destinations")

with st.expander("🔍 Search & Filter Controls", expanded=True):
    r1_col1, r1_col2, r1_col3, r1_col4 = st.columns([1.8, 1, 1, 1])
    with r1_col1:
        query_text = st.text_input("Search destination, monument, or region", placeholder="e.g. Jaipur, Eiffel Tower, Goa, Tokyo...")
    with r1_col2:
        origin_city = st.text_input("Your Starting City", value="Delhi", help="Used to estimate outbound and return transportation costs.")
    with r1_col3:
        scope = st.selectbox("Travel Scope", ["All", "Domestic", "International"])
    with r1_col4:
        budget_tier = st.selectbox("Budget Tier", ["All", "Budget", "Moderate", "Luxury"])

    r2_col1, r2_col2, r2_col3, r2_col4 = st.columns(4)
    with r2_col1:
        countries = ["All"] + get_distinct_countries(scope=scope)
        selected_country = st.selectbox("Country", countries)
    with r2_col2:
        dest_types = ["All"] + get_distinct_destination_types()
        selected_type = st.selectbox("Destination Type", dest_types)
    with r2_col3:
        filter_days = st.number_input("Trip Duration (Days)", min_value=1, max_value=30, value=3, step=1)
    with r2_col4:
        filter_travelers = st.number_input("Travelers Count", min_value=1, max_value=20, value=2, step=1)

filtered_df = search_destinations(
    query=query_text,
    scope=scope,
    country=None if selected_country == "All" else selected_country,
    destination_type=None if selected_type == "All" else selected_type,
    budget_category=None if budget_tier == "All" else budget_tier
)

st.caption(f"Displaying **{len(filtered_df)}** destinations. Origin set to **{origin_city}**.")

# -------------------------------------------------------------
# Active Budget Preview Drawer (if selected)
# -------------------------------------------------------------
if "preview_dest_id" in st.session_state and st.session_state["preview_dest_id"]:
    preview_dest = get_destination_by_id(st.session_state["preview_dest_id"])
    if preview_dest:
        with st.container(border=True):
            st.markdown(f"### 📊 Detailed Budget Preview: {preview_dest['destination_name']} ({preview_dest['country']})")
            st.caption(f"Origin: **{origin_city}** | Duration: **{filter_days} Days** | Travelers: **{filter_travelers}** | Price Status: `{preview_dest.get('price_status', 'Estimated')}`")
            
            p_req = BudgetRequestSchema(
                destination_id=preview_dest["destination_id"],
                starting_location=origin_city,
                num_travelers=filter_travelers,
                num_days=filter_days,
                transport_mode="Train (Express / AC)" if preview_dest.get("is_domestic") else "Flight",
                accommodation_tier="Mid-range 3-Star Hotel",
                food_tier="Casual Dining & Cafes",
                local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
                activities_level="Moderate Sightseeing",
                contingency_percent=10.0
            )
            p_budget = calc.calculate_trip_budget(p_req)

            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            with col_m1:
                st.metric("Total Estimated Cost", f"INR {p_budget['total_estimated_cost_inr']:,.0f}")
            with col_m2:
                st.metric("Cost per Traveler", f"INR {p_budget['per_person_cost_inr']:,.0f}")
            with col_m3:
                st.metric("Round-Trip Transit", f"INR {p_budget['breakdown']['Total Transportation']:,.0f}")
            with col_m4:
                st.metric("Lodging Subtotal", f"INR {p_budget['breakdown']['Accommodation']:,.0f}")

            with st.expander("View Full Category Itemization & Search Links", expanded=True):
                c_tbl, c_lnks = st.columns([1.5, 1])
                with c_tbl:
                    itemized = [
                        {"Expense Category": k, "Amount (INR)": f"INR {v:,.0f}"}
                        for k, v in p_budget["breakdown"].items()
                    ]
                    st.dataframe(pd.DataFrame(itemized), hide_index=True, use_container_width=True)
                with c_lnks:
                    st.markdown("**Real-Time Search Links:**")
                    for title, url in p_budget["route_logistics"].get("search_links", {}).items():
                        st.markdown(f"• [{title}]({url})")

            btn_col1, btn_col2 = st.columns([2, 1])
            with btn_col1:
                if st.button("🚀 Plan This Trip in AI Trip Planner", type="primary", use_container_width=True):
                    st.session_state["selected_dest_id"] = preview_dest["destination_id"]
                    st.session_state["planner_origin_city"] = origin_city
                    st.session_state["planner_days"] = filter_days
                    st.session_state["planner_travelers"] = filter_travelers
                    st.session_state["planner_budget"] = p_budget["total_estimated_cost_inr"]
                    st.switch_page("pages/2_AI_Trip_Planner.py")
            with btn_col2:
                if st.button("Close Preview", use_container_width=True):
                    st.session_state["preview_dest_id"] = None
                    st.rerun()

# -------------------------------------------------------------
# Section E: Destination Comparison Feature
# -------------------------------------------------------------
with st.expander("⚖️ Compare Destinations Side-by-Side", expanded=False):
    dest_names_all = [r["destination_name"] for _, r in get_all_destinations().iterrows()]
    selected_compare = st.multiselect("Select 2 to 4 destinations to compare:", dest_names_all, default=["Jaipur", "Goa"])
    
    if len(selected_compare) >= 2:
        comp_rows = []
        for dname in selected_compare:
            match = get_all_destinations()[get_all_destinations()["destination_name"] == dname]
            if not match.empty:
                dest_row = match.iloc[0].to_dict()
                d_id = dest_row["destination_id"]
                c_req = BudgetRequestSchema(
                    destination_id=d_id,
                    starting_location=origin_city,
                    num_travelers=filter_travelers,
                    num_days=filter_days,
                    transport_mode="Train (Express / AC)" if dest_row.get("is_domestic") else "Flight",
                    accommodation_tier="Mid-range 3-Star Hotel",
                    food_tier="Casual Dining & Cafes",
                    local_transport_tier="Auto Rickshaw / Taxi / Rideshare",
                    activities_level="Moderate Sightseeing",
                    contingency_percent=10.0
                )
                b_res = calc.calculate_trip_budget(c_req)
                comp_rows.append({
                    "Destination": f"{dest_row['destination_name']} ({dest_row['country']})",
                    "Price Status": dest_row.get("price_status", "Estimated"),
                    "Transit from Origin": f"INR {b_res['breakdown']['Total Transportation']:,.0f}",
                    "Nightly Lodging": f"INR {b_res['breakdown']['Accommodation'] / max(1, filter_days-1):,.0f}",
                    "Daily Food & Transit": f"INR {(b_res['breakdown']['Food & Dining'] + b_res['breakdown']['Local Transportation']) / filter_days:,.0f}",
                    "Total Trip Cost": f"INR {b_res['total_estimated_cost_inr']:,.0f}",
                    "Recommended Duration": f"{dest_row['recommended_duration_days']} Days",
                    "Ideal Season": dest_row.get("best_season", "All Year")
                })
        st.dataframe(pd.DataFrame(comp_rows), hide_index=True, use_container_width=True)
    else:
        st.info("Please pick at least two destinations to view a side-by-side comparison.")

# -------------------------------------------------------------
# Main Catalog: Card View & Map View
# -------------------------------------------------------------
view_tab, map_tab = st.tabs(["🗂️ Destination Cards", "🌍 Interactive World Map"])

with map_tab:
    st.markdown("#### Geographic Map of Filtered Destinations")
    if not filtered_df.empty:
        records = filtered_df.to_dict(orient="records")
        fmap = create_multi_destination_map(records)
        st_folium(fmap, width=1200, height=520)
    else:
        st.warning("No destinations match the current filters to display on the map.")

with view_tab:
    dest_records = filtered_df.to_dict(orient="records")
    
    # Pagination
    items_per_page = 9
    total_pages = max(1, (len(dest_records) + items_per_page - 1) // items_per_page)
    
    if total_pages > 1:
        p_col1, p_col2 = st.columns([1, 4])
        with p_col1:
            page_num = st.number_input(f"Page (1 to {total_pages})", min_value=1, max_value=total_pages, value=1, step=1)
    else:
        page_num = 1
        
    start_idx = (page_num - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_records = dest_records[start_idx:end_idx]

    cols = st.columns(3)
    for i, dest in enumerate(page_records):
        with cols[i % 3]:
            with st.container(border=True):
                dom_label = "🇮🇳 Domestic" if dest.get("is_domestic") else "✈️ International"
                badge_class = "badge-domestic" if dest.get("is_domestic") else "badge-intl"
                
                p_status = dest.get("price_status", "Estimated")
                status_class = "badge-verified" if p_status == "Verified" else "badge-estimated"

                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                    <span class="badge-pill {badge_class}">{dom_label}</span>
                    <span class="badge-pill {status_class}">● {p_status}</span>
                </div>
                <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">
                    {dest['destination_name']}
                </div>
                <div style="font-size: 0.84rem; color: #64748b; margin-bottom: 8px;">
                    📍 {dest['region']}, {dest['country']} • {dest['destination_type']}
                </div>
                """, unsafe_allow_html=True)
                
                img_src = dest.get("image_url") or "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"
                st.image(img_src, use_container_width=True)
                
                st.write(dest['description'])

                # Compute approximate origin transport & total cost for selected duration and travelers
                approx_route = calculate_journey_logistics(
                    origin_city=origin_city,
                    destination_id=dest["destination_id"],
                    transport_mode="Train (Express / AC)" if dest.get("is_domestic") else "Flight",
                    num_travelers=filter_travelers
                )
                
                nightly_room = float(dest.get("accommodation_budget_per_night", 2500.0))
                daily_food = float(dest.get("food_budget_per_person_per_day", 800.0))
                daily_transit = float(dest.get("local_transport_budget_per_day", 400.0))
                daily_sight = float(dest.get("sightseeing_budget_per_person_per_day", 400.0))
                
                num_nights = max(0, filter_days - 1)
                rooms = (filter_travelers + 1) // 2
                
                est_lodging = nightly_room * rooms * num_nights
                est_living = (daily_food * filter_travelers + daily_transit + daily_sight * filter_travelers) * filter_days
                est_total = approx_route["total_transport_cost_inr"] + est_lodging + est_living
                
                st.markdown(f"""
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Daily Living:</span>
                        <span style="font-weight: 800; color: #0f766e; font-size: 0.92rem;">INR {dest['estimated_daily_budget_inr']:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3px;">
                        <span style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Nightly Lodging:</span>
                        <span style="font-weight: 800; color: #0284c7; font-size: 0.92rem;">INR {nightly_room:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 3px;">
                        <span style="font-size: 0.82rem; color: #64748b; font-weight: 600;">Round-Trip Transit:</span>
                        <span style="font-weight: 700; color: #334155; font-size: 0.86rem;">INR {approx_route['total_transport_cost_inr']:,.0f}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px; padding-top: 4px; border-top: 1px dashed #cbd5e1;">
                        <span style="font-size: 0.84rem; color: #0f172a; font-weight: 700;">Est. Total ({filter_days}D/{filter_travelers}P):</span>
                        <span style="font-weight: 900; color: #0d9488; font-size: 1.05rem;">INR {est_total:,.0f}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("Attractions & Ticket Prices"):
                    attrs = get_attractions_for_destination(dest["destination_id"])
                    if attrs:
                        for a in attrs[:4]:
                            ad_p = a.get("adult_ticket_price", a.get("estimated_ticket_inr", 0))
                            badge = f"INR {ad_p:,.0f}" if ad_p > 0 else "Free"
                            st.markdown(f"• **{a['attraction_name']}** — `{badge}` ({a.get('price_status', 'Estimated')})")
                    else:
                        st.write(dest.get("key_attractions", "City center sights"))

                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    if st.button("Budget Details", key=f"btn_prev_{dest['destination_id']}", use_container_width=True):
                        st.session_state["preview_dest_id"] = dest["destination_id"]
                        st.rerun()
                with col_b2:
                    if st.button("Plan Trip", key=f"btn_explore_{dest['destination_id']}", use_container_width=True, type="primary"):
                        st.session_state["selected_dest_id"] = dest["destination_id"]
                        st.session_state["planner_origin_city"] = origin_city
                        st.session_state["planner_days"] = filter_days
                        st.session_state["planner_travelers"] = filter_travelers
                        st.session_state["planner_budget"] = est_total
                        st.switch_page("pages/2_AI_Trip_Planner.py")
