"""My Trips - Saved Itineraries Manager and Export Center."""

import streamlit as st
import json

from src.config import APP_NAME
from src.trip_storage import (
    get_all_trips,
    get_trip_by_id,
    update_trip_title,
    delete_trip
)
from src.export_service import export_trip_to_pdf, export_itinerary_to_csv, export_trip_to_json
from src.style_service import apply_custom_theme, render_sidebar_brand

st.set_page_config(
    page_title=f"My Trips — {APP_NAME}",
    page_icon="🧳",
    layout="wide"
)

apply_custom_theme()
render_sidebar_brand()

st.title("🧳 My Saved Trips")
st.markdown("Access, edit, and export your saved travel plans stored locally in your SQLite database.")

trips = get_all_trips()

if not trips:
    st.info("You don't have any saved itineraries yet.")
    st.markdown("Use the **AI Trip Planner** to generate a custom itinerary and click **Save to My Trips**.")
    if st.button("🚀 Plan a Trip Now", type="primary"):
        st.switch_page("pages/2_AI_Trip_Planner.py")
else:
    st.caption(f"You have **{len(trips)}** saved journey(s).")
    
    for t in trips:
        trip_id = t["trip_id"]
        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"### {t['title']}")
                st.caption(f"📍 Destination: **{t['destination_name']}** | 📅 Starts: **{t['start_date']}** | ⏱️ **{t['duration_days']} Days** | 👥 **{t['travelers_count']} Traveler(s)**")
            with head_col2:
                cost_val = t.get("total_cost_inr", 0.0)
                st.markdown(f"<div style='text-align: right; color: #0d9488; font-size: 1.25rem; font-weight: 800;'>INR {cost_val:,.0f}</div>", unsafe_allow_html=True)
                st.caption(f"<div style='text-align: right;'>Saved: {t['created_at'][:10]}</div>", unsafe_allow_html=True)

            # Details & Actions Expander
            with st.expander(f"View Itinerary Details & Export Options ({trip_id})"):
                full_trip = get_trip_by_id(trip_id)
                if full_trip:
                    itin = full_trip.get("itinerary", {})
                    
                    # Schedule overview
                    st.markdown("#### Schedule Overview")
                    for day in itin.get("days", []):
                        st.markdown(f"**Day {day.get('day_number')}: {day.get('theme')}** ({day.get('date')})")
                        for act in day.get("activities", []):
                            st.write(f"• `{act.get('slot')}`: **{act.get('title')}** — {act.get('description')}")
                        st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)

                    st.divider()

                    # Rename Title & Export Row
                    st.markdown("#### Actions & Exports")
                    r_col1, r_col2 = st.columns([2, 2])
                    
                    with r_col1:
                        new_title = st.text_input("Rename Trip Title", value=t["title"], key=f"title_{trip_id}")
                        if st.button("Update Title", key=f"btn_upd_{trip_id}"):
                            if new_title.strip():
                                update_trip_title(trip_id, new_title.strip())
                                st.success("Title updated!")
                                st.rerun()

                    with r_col2:
                        pdf_data = export_trip_to_pdf(itin, full_trip.get("budget", {}))
                        csv_data = export_itinerary_to_csv(itin)
                        json_data = export_trip_to_json(itin)
                        
                        btn_c1, btn_c2, btn_c3 = st.columns(3)
                        with btn_c1:
                            st.download_button(
                                "📄 PDF",
                                data=pdf_data,
                                file_name=f"{trip_id}_{t['destination_name']}.pdf",
                                mime="application/pdf",
                                key=f"pdf_{trip_id}",
                                use_container_width=True
                            )
                        with btn_c2:
                            st.download_button(
                                "📊 CSV",
                                data=csv_data,
                                file_name=f"{trip_id}_{t['destination_name']}.csv",
                                mime="text/csv",
                                key=f"csv_{trip_id}",
                                use_container_width=True
                            )
                        with btn_c3:
                            st.download_button(
                                "⚙️ JSON",
                                data=json_data,
                                file_name=f"{trip_id}_{t['destination_name']}.json",
                                mime="application/json",
                                key=f"json_{trip_id}",
                                use_container_width=True
                            )

                    st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
                    if st.button(f"🗑️ Delete Trip ({trip_id})", key=f"del_{trip_id}", type="secondary"):
                        delete_trip(trip_id)
                        st.warning(f"Trip {trip_id} deleted.")
                        st.rerun()
