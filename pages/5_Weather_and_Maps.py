"""Weather & Maps Explorer - Real-Time Meteorological Forecasts & Geospatial Sights."""

import streamlit as st
from streamlit_folium import st_folium

from src.config import APP_NAME
from src.data_loader import get_all_destinations, get_destination_by_id
from src.weather_service import get_weather_forecast
from src.map_service import create_destination_map
from src.style_service import apply_custom_theme, render_sidebar_brand

st.set_page_config(
    page_title=f"Weather & Maps — {APP_NAME}",
    page_icon="🌤️",
    layout="wide"
)

apply_custom_theme()
render_sidebar_brand()

st.title("🌤️ Weather & Maps")
st.markdown("Check live weather forecasts via Open-Meteo and explore interactive attraction maps for any destination.")

all_dests_df = get_all_destinations()
dest_dict = {
    f"{r['destination_name']} ({r['country']})": r["destination_id"]
    for _, r in all_dests_df.iterrows()
}

selected_label = st.selectbox("Select Destination to Inspect", list(dest_dict.keys()), index=0)
chosen_dest_id = dest_dict[selected_label]
dest_info = get_destination_by_id(chosen_dest_id)

st.divider()

# Fetch Weather
weather_data = get_weather_forecast(chosen_dest_id)

# -------------------------------------------------------------
# 1. Weather Forecast Section
# -------------------------------------------------------------
st.subheader(f"1. Meteorological Forecast: {weather_data['destination_name']}")

badge_type = "success" if weather_data["is_live"] else "info"
st.caption(f"📡 **Data Source:** {weather_data['source']} — *{weather_data['status_message']}*")

if weather_data.get("current"):
    curr = weather_data["current"]
    w_col1, w_col2, w_col3, w_col4 = st.columns(4)
    with w_col1:
        st.metric("Current Temp", f"{curr['temperature_c']} °C", f"Feels like {curr['feels_like_c']} °C")
    with w_col2:
        st.metric("Condition", f"{curr['icon']} {curr['condition']}")
    with w_col3:
        st.metric("Humidity", f"{curr['humidity_percent']}%")
    with w_col4:
        st.metric("Wind Speed", f"{curr['wind_speed_kmh']} km/h")

# 7-Day Forecast Cards
if weather_data.get("daily_forecast"):
    st.markdown("#### 7-Day Forecast")
    day_cols = st.columns(len(weather_data["daily_forecast"]))
    for i, d in enumerate(weather_data["daily_forecast"]):
        with day_cols[i]:
            with st.container(border=True):
                st.markdown(f"**{d['date'][-5:]}**")
                st.markdown(f"<div style='font-size: 1.8rem; text-align: center;'>{d['icon']}</div>", unsafe_allow_html=True)
                st.caption(f"<div style='text-align: center;'>{d['condition']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div style='text-align: center; font-weight: bold;'>{d['max_temp_c']}° / {d['min_temp_c']}°</div>", unsafe_allow_html=True)
                if d.get("precipitation_mm", 0) > 0:
                    st.caption(f"🌧️ {d['precipitation_mm']} mm")

# Climate Profile
st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    cl_col1, cl_col2 = st.columns([2, 1])
    with cl_col1:
        st.markdown(f"**Historical Climate Profile:** {weather_data.get('climate_summary', '')}")
    with cl_col2:
        st.markdown(f"**Optimal Visiting Season:** `{weather_data.get('best_season', '')}`")

st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Interactive Map Section
# -------------------------------------------------------------
st.subheader(f"2. Sights & Local Geography: {weather_data['destination_name']}")

fmap = create_destination_map(chosen_dest_id)
if fmap:
    st_folium(fmap, width=1200, height=520)
else:
    st.warning("Map coordinates unavailable for this destination.")

# Action CTA
st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)
if st.button(f"📅 Create Itinerary for {weather_data['destination_name']}", type="primary"):
    st.session_state["selected_dest_id"] = chosen_dest_id
    st.switch_page("pages/2_AI_Trip_Planner.py")
