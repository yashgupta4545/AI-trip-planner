"""Realistic Travel Budget Calculator - Granular Expense Estimation & Feasibility Analysis."""

from datetime import date, timedelta
import streamlit as st
import plotly.express as px
import pandas as pd

from src.config import (
    APP_NAME, ACCOMMODATION_TIERS, TRANSPORT_MODES
)
from src.data_loader import get_all_destinations, get_destination_by_id
from src.data_validation import BudgetRequestSchema
from src.budget_calculator import BudgetCalculator
from src.export_service import export_budget_to_csv, export_budget_to_pdf, export_trip_to_json
from src.style_service import apply_custom_theme, render_sidebar_brand

st.set_page_config(
    page_title=f"Travel Budget — {APP_NAME}",
    page_icon="💰",
    layout="wide"
)

apply_custom_theme()
render_sidebar_brand()

st.title("💰 Travel Budget & Cost Calculator")
st.markdown("Estimate travel expenses transparently with real itemized category breakdowns, route transit logistics, and shortfall alerts.")

all_dests_df = get_all_destinations()
dest_dict = {
    f"{r['destination_name']} ({r['country']})": r["destination_id"]
    for _, r in all_dests_df.iterrows()
}

# Check incoming session state from Explore Destinations or AI Trip Planner
pre_dest = st.session_state.get("budget_calc_dest_id", None)
pre_origin = st.session_state.get("budget_calc_origin", "Delhi")
pre_days = st.session_state.get("budget_calc_days", 4)
pre_travelers = st.session_state.get("budget_calc_travelers", 2)
pre_adults = st.session_state.get("budget_calc_adults", max(1, pre_travelers))
pre_children = st.session_state.get("budget_calc_children", 0)
pre_transport = st.session_state.get("budget_calc_transport", "Flight")
pre_target = st.session_state.get("budget_calc_target", 0.0)

default_dest_idx = 0
options_list = list(dest_dict.keys())
if pre_dest:
    for idx, (label, d_id) in enumerate(dest_dict.items()):
        if d_id == pre_dest:
            default_dest_idx = idx
            break

# -------------------------------------------------------------
# 1. Parameter Form
# -------------------------------------------------------------
with st.container(border=True):
    st.subheader("1. Journey Details & Preferences")
    
    c1, c2, c3, c4 = st.columns([1.8, 1.2, 1, 1])
    with c1:
        selected_dest_label = st.selectbox("Destination", options_list, index=default_dest_idx)
        chosen_dest_id = dest_dict[selected_dest_label]
    with c2:
        origin_city = st.text_input("Starting City / Origin", value=pre_origin)
    with c3:
        num_adults = st.number_input("Adults", min_value=1, max_value=30, value=int(pre_adults), step=1)
    with c4:
        num_children = st.number_input("Children", min_value=0, max_value=20, value=int(pre_children), step=1)

    tot_travelers = num_adults + num_children

    r2_c1, r2_c2, r2_c3, r2_c4 = st.columns(4)
    with r2_c1:
        start_date = st.date_input("Departure Date", value=date.today() + timedelta(days=7), min_value=date.today())
    with r2_c2:
        num_days = st.number_input("Trip Duration (Days)", min_value=1, max_value=60, value=int(pre_days), step=1)
    with r2_c3:
        trans_idx = TRANSPORT_MODES.index(pre_transport) if pre_transport in TRANSPORT_MODES else 0
        transport_mode = st.selectbox("Intercity Transport Mode", TRANSPORT_MODES, index=trans_idx)
    with r2_c4:
        accommodation_tier = st.selectbox("Accommodation Tier", ACCOMMODATION_TIERS, index=2)

    # Personal vehicle parameters if personal vehicle selected
    mileage_val = 15.0
    fuel_price_val = 95.0
    if transport_mode in ["Personal Vehicle / Car", "Self-drive / Rental Car"]:
        pv_c1, pv_c2 = st.columns(2)
        with pv_c1:
            mileage_val = st.number_input("Vehicle Mileage (km / Liter)", min_value=5.0, max_value=40.0, value=15.0, step=1.0)
        with pv_c2:
            fuel_price_val = st.number_input("Fuel Price (INR / Liter)", min_value=60.0, max_value=200.0, value=95.0, step=2.0)

    r3_c1, r3_c2, r3_c3, r3_c4 = st.columns(4)
    with r3_c1:
        food_tier = st.selectbox(
            "Food & Dining Tier",
            ["Street Food & Local Dhabas", "Casual Dining & Cafes", "Fine Dining & Multi-Cuisine"],
            index=1
        )
    with r3_c2:
        local_transit_tier = st.selectbox(
            "Local Transportation",
            ["Walking & Public Transit", "Auto Rickshaw / Taxi / Rideshare", "Chauffeured Private Car"],
            index=1
        )
    with r3_c3:
        activities_tier = st.selectbox(
            "Sightseeing & Attractions",
            ["Free & Self-Guided", "Moderate Sightseeing", "All-Inclusive & Adventure Sports"],
            index=1
        )
    with r3_c4:
        contingency_pct = st.slider("Contingency Buffer (%)", min_value=0.0, max_value=30.0, value=10.0, step=2.5)

    st.markdown("---")
    c_target, _ = st.columns([1.5, 2.5])
    with c_target:
        user_target_budget = st.number_input(
            "Your Target / Max Budget (INR, Optional)",
            min_value=0.0,
            max_value=2000000.0,
            value=float(pre_target) if pre_target else 0.0,
            step=5000.0,
            help="Leave as 0 if you want to calculate the cost without comparing against a budget constraint."
        )

# -------------------------------------------------------------
# 2. Calculation & Visual Dashboard
# -------------------------------------------------------------
calc = BudgetCalculator()
req = BudgetRequestSchema(
    destination_id=chosen_dest_id,
    starting_location=origin_city,
    num_travelers=tot_travelers,
    num_adults=num_adults,
    num_children=num_children,
    num_days=num_days,
    transport_mode=transport_mode,
    accommodation_tier=accommodation_tier,
    food_tier=food_tier,
    local_transport_tier=local_transit_tier,
    activities_level=activities_tier,
    contingency_percent=contingency_pct,
    user_target_budget=user_target_budget if user_target_budget > 0 else None,
    personal_vehicle_mileage_kmpl=mileage_val,
    personal_vehicle_fuel_price_inr=fuel_price_val
)

budget_result = calc.calculate_trip_budget(req)

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.subheader(f"2. Cost Breakdown: {budget_result['origin_city']} ⇄ {budget_result['destination_name']}")

# Top Metrics Row
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Total Estimated Cost", f"INR {budget_result['total_estimated_cost_inr']:,.0f}")
with m2:
    st.metric("Cost per Traveler", f"INR {budget_result['per_person_cost_inr']:,.0f}")
with m3:
    st.metric("Accommodation Subtotal", f"INR {budget_result['breakdown']['Accommodation']:,.0f}")
with m4:
    st.metric("Transportation Subtotal", f"INR {budget_result['breakdown']['Total Transportation']:,.0f}")

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# Shortfall / Feasibility Card
sf = budget_result["shortfall_analysis"]
if sf["status"] == "Healthy Budget":
    st.success(f"✅ **{sf['status']}**: {sf['message']}")
elif sf["status"] == "Budget Shortfall":
    st.error(f"⚠️ **{sf['status']}**: {sf['message']}")
    with st.expander("💡 Cost Optimization & Saving Recommendations", expanded=True):
        st.write(f"**Top Cost Drivers:** {', '.join(sf.get('top_cost_drivers', []))}")
        st.markdown("**Suggestions:**")
        for s in sf.get("suggestions", []):
            st.markdown(f"• {s}")

# Visual Chart & Itemized Table
col_chart, col_table = st.columns([1.3, 1.7])

with col_chart:
    st.markdown("#### Expense Allocation")
    chart_data = {
        "Category": [
            "Transportation",
            "Accommodation",
            "Food & Dining",
            "Local Transit",
            "Attractions & Entry",
            "Misc & Shopping",
            "Contingency"
        ],
        "Amount (INR)": [
            budget_result["breakdown"]["Total Transportation"],
            budget_result["breakdown"]["Accommodation"],
            budget_result["breakdown"]["Food & Dining"],
            budget_result["breakdown"]["Local Transportation"],
            budget_result["breakdown"]["Attractions & Sightseeing"],
            budget_result["breakdown"]["Miscellaneous & Shopping"],
            budget_result["breakdown"]["Contingency Reserve"]
        ]
    }
    df_chart = pd.DataFrame(chart_data)
    fig = px.pie(
        df_chart,
        values="Amount (INR)",
        names="Category",
        hole=0.45,
        color_discrete_sequence=["#0284c7", "#0d9488", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#64748b"]
    )
    fig.update_layout(margin=dict(t=10, b=10, l=10, r=10), height=340)
    st.plotly_chart(fig, use_container_width=True)

with col_table:
    st.markdown("#### Detailed Itemization")
    table_rows = []
    for k, v in budget_result["breakdown"].items():
        pct = (v / max(1.0, budget_result["total_estimated_cost_inr"])) * 100.0
        table_rows.append({
            "Expense Category": k,
            "Amount (INR)": f"INR {v:,.2f}",
            "Share (%)": f"{pct:.1f}%"
        })
    df_table = pd.DataFrame(table_rows)
    st.dataframe(df_table, use_container_width=True, hide_index=True)

# Route & External Search Links
route_info = budget_result.get("route_logistics", {})
with st.expander("📍 Route Logistics & External Search Links", expanded=True):
    r_col1, r_col2 = st.columns([1.5, 1])
    with r_col1:
        st.markdown(f"""
        - **Route:** {route_info.get('origin_city')} to {route_info.get('destination_name')}
        - **Distance:** {route_info.get('travel_distance_km', 0):,.0f} km ({route_info.get('transport_mode')})
        - **Outbound Travel:** INR {route_info.get('outbound_cost_inr', 0):,.2f} (~{route_info.get('outbound_duration_hours', 2)} hrs)
        - **Return Travel:** INR {route_info.get('return_cost_inr', 0):,.2f} (~{route_info.get('return_duration_hours', 2)} hrs)
        - **Assumptions:** {route_info.get('assumptions')}
        - **Price Status:** `{route_info.get('price_status', 'Estimated')}`
        """)
    with r_col2:
        st.markdown("**Real-Time Fare & Ticket Searches:**")
        for title, url in route_info.get("search_links", {}).items():
            st.markdown(f"• [{title}]({url})")

# Assumptions
with st.expander("ℹ️ Estimation Assumptions & Data Sources"):
    for a in budget_result["assumptions"]:
        st.markdown(f"• {a}")

# -------------------------------------------------------------
# 3. Export Section (PDF, CSV, JSON)
# -------------------------------------------------------------
st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
st.subheader("3. Export Your Budget Estimate")

col_exp_csv, col_exp_json, col_exp_pdf = st.columns(3)

with col_exp_csv:
    csv_budget = export_budget_to_csv(budget_result)
    st.download_button(
        label="📊 Download Budget CSV",
        data=csv_budget,
        file_name=f"TripGenie_Budget_{budget_result['destination_name']}_{budget_result['num_days']}D.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp_json:
    json_budget = export_trip_to_json(budget_result)
    st.download_button(
        label="⚙️ Download Budget JSON",
        data=json_budget,
        file_name=f"TripGenie_Budget_{budget_result['destination_name']}_{budget_result['num_days']}D.json",
        mime="application/json",
        use_container_width=True
    )

with col_exp_pdf:
    pdf_budget = export_budget_to_pdf(budget_result)
    st.download_button(
        label="📄 Download Budget PDF",
        data=pdf_budget,
        file_name=f"TripGenie_Budget_{budget_result['destination_name']}_{budget_result['num_days']}D.pdf",
        mime="application/pdf",
        use_container_width=True
    )
