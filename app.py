"""TripGenie AI - Intelligent Travel Planning & Recommendation Platform.
Main Application & Discovery Dashboard.
"""

import streamlit as st
import pandas as pd
from src.config import (
    APP_NAME, APP_TAGLINE, APP_VERSION,
    COLOR_PRIMARY, COLOR_PRIMARY_DARK, COLOR_PRIMARY_LIGHT,
    COLOR_BG, COLOR_CARD_BG, COLOR_TEXT_MAIN, COLOR_TEXT_MUTED
)
from src.data_loader import (
    get_all_destinations,
    get_dataset_summary,
    get_distinct_interests,
    search_destinations
)
from src.recommendation_engine import DestinationRecommender
from src.data_validation import RecommendationQuerySchema
from src.style_service import apply_custom_theme, render_sidebar_brand

# Streamlit Page Configuration
st.set_page_config(
    page_title=f"{APP_NAME} — {APP_TAGLINE}",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Master Luxury Theme & Sidebar Brand
apply_custom_theme()
render_sidebar_brand()

# Application Summary Metrics
stats = get_dataset_summary()

# -------------------------------------------------------------
# 1. Luxury Hero Banner & Primary Navigation Actions
# -------------------------------------------------------------
st.markdown(f"""
<div class="hero-container">
    <div class="hero-badge">✨ AI-Powered Intelligent Travel Companion v{APP_VERSION}</div>
    <div class="hero-title">
        {APP_NAME} — <span class="hero-gradient-text">Plan Real Journeys</span>
    </div>
    <div class="hero-subtitle">{APP_TAGLINE}</div>
    <div class="hero-desc">
        Explore {stats['total_destinations']} verified destinations in India and {stats['total_countries']} countries worldwide. 
        Experience realistic destination-specific pricing, door-to-door transit logistics, 
        and personalized day-by-day schedules with zero mandatory paid APIs.
    </div>
    <div class="hero-chips-container">
        <span class="hero-chip">🗺️ {stats['total_destinations']} Destinations</span>
        <span class="hero-chip">🚆 Multi-Modal Transit</span>
        <span class="hero-chip">💰 Centralized Budgeting</span>
        <span class="hero-chip">🌤️ Live Weather Forecasts</span>
        <span class="hero-chip">📄 PDF & CSV Downloads</span>
    </div>
    <div class="hero-action-row" style="display: flex; gap: 16px; margin-top: 26px; flex-wrap: wrap; align-items: center;">
        <a href="/AI_Trip_Planner" target="_self" class="hero-btn-primary" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: #ffffff !important; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.05rem; padding: 13px 28px; border-radius: 12px; text-decoration: none !important; box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45); border: 1px solid rgba(255, 255, 255, 0.25); cursor: pointer;">
            <span style="color: #ffffff !important; text-decoration: none !important;">✈️ Plan My Trip</span>
        </a>
        <a href="/Explore_Destinations" target="_self" class="hero-btn-secondary" style="display: inline-flex; align-items: center; justify-content: center; gap: 8px; background: rgba(255, 255, 255, 0.16); backdrop-filter: blur(14px); -webkit-backdrop-filter: blur(14px); color: #ffffff !important; font-family: 'Plus Jakarta Sans', sans-serif; font-weight: 700; font-size: 1.05rem; padding: 13px 28px; border-radius: 12px; text-decoration: none !important; border: 1.5px solid rgba(255, 255, 255, 0.5); box-shadow: 0 4px 14px rgba(0, 0, 0, 0.15); cursor: pointer;">
            <span style="color: #ffffff !important; text-decoration: none !important;">🌍 Explore Destinations</span>
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# -------------------------------------------------------------
# 2. Quick Statistics Grid (Modern Floating Glass Cards)
# -------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
with c1:
    st.markdown(f"""
    <div class="stat-card-luxury">
        <div class="stat-icon-wrap">🌐</div>
        <div class="stat-number-luxury">{stats['total_destinations']}</div>
        <div class="stat-label-luxury">Destinations</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="stat-card-luxury">
        <div class="stat-icon-wrap">🇮🇳</div>
        <div class="stat-number-luxury">{stats['domestic_destinations']}</div>
        <div class="stat-label-luxury">India Domestic</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    st.markdown(f"""
    <div class="stat-card-luxury">
        <div class="stat-icon-wrap">✈️</div>
        <div class="stat-number-luxury">{stats['international_destinations']}</div>
        <div class="stat-label-luxury">International</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    st.markdown(f"""
    <div class="stat-card-luxury">
        <div class="stat-icon-wrap">🏛️</div>
        <div class="stat-number-luxury">{stats['total_countries']}</div>
        <div class="stat-label-luxury">Countries</div>
    </div>
    """, unsafe_allow_html=True)
with c5:
    st.markdown(f"""
    <div class="stat-card-luxury">
        <div class="stat-icon-wrap">🎟️</div>
        <div class="stat-number-luxury">{stats['total_attractions']}</div>
        <div class="stat-label-luxury">Key Sights</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 3. Quick Search & Preference Discovery Section
# -------------------------------------------------------------
st.subheader("🔍 Find Your Ideal Getaway")

with st.container(border=True):
    col_search, col_scope, col_style = st.columns([3, 1.2, 1.2])
    with col_search:
        search_q = st.text_input(
            "Search destinations, monuments, or activities",
            placeholder="e.g. Jaipur, Taj Mahal, Scuba Diving, Mountains, Paris, Tokyo...",
            label_visibility="collapsed"
        )
    with col_scope:
        scope_sel = st.selectbox("Travel Scope", ["All", "Domestic", "International"], label_visibility="collapsed")
    with col_style:
        budget_sel = st.selectbox("Budget Tier", ["All", "Budget", "Moderate", "Luxury"], label_visibility="collapsed")

    # Quick tags
    common_interests = ["Heritage", "Beach", "Mountains", "Wildlife", "Culinary", "Adventure"]
    selected_tag = st.pills("Popular Interests", ["All"] + common_interests, default="All")
    actual_tag = None if selected_tag == "All" else selected_tag

filtered_df = search_destinations(
    query=search_q,
    scope=scope_sel,
    budget_category=None if budget_sel == "All" else budget_sel,
    selected_interest=actual_tag
)

st.caption(f"Showing **{len(filtered_df)}** matching destinations across the world")

# -------------------------------------------------------------
# 4. Featured Destination Cards
# -------------------------------------------------------------
display_limit = 6
display_records = filtered_df.head(display_limit).to_dict(orient="records")

cols = st.columns(3)
for i, dest in enumerate(display_records):
    col = cols[i % 3]
    with col:
        with st.container(border=True):
            dom_badge = "🇮🇳 Domestic" if dest.get("is_domestic") else "✈️ International"
            badge_class = "badge-domestic" if dest.get("is_domestic") else "badge-intl"
            
            p_status = dest.get("price_status", "Estimated")
            status_class = "badge-verified" if p_status == "Verified" else "badge-estimated"
            
            img = dest.get("image_url") or "https://images.unsplash.com/photo-1488646953014-85cb44e25828?w=800"

            st.markdown(f"""
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;">
                <span class="badge-pill {badge_class}">{dom_badge}</span>
                <span class="badge-pill {status_class}">● {p_status}</span>
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.3rem; font-weight: 800; color: #0f172a; margin-bottom: 2px;">
                {dest['destination_name']}
            </div>
            <div style="font-size: 0.85rem; color: #64748b; margin-bottom: 8px;">
                📍 {dest['region']}, {dest['country']} • {dest['destination_type']}
            </div>
            """, unsafe_allow_html=True)
            
            st.image(img, use_container_width=True)
            
            st.write(dest['description'])
            
            daily_cost = float(dest.get('estimated_daily_budget_inr', 2500))
            lodging_cost = float(dest.get('accommodation_budget_per_night', 2500))
            
            st.markdown(f"""
            <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 10px 14px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Daily Living:</span>
                    <span style="font-weight: 800; color: #0f766e; font-size: 0.95rem;">INR {daily_cost:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Nightly Room:</span>
                    <span style="font-weight: 800; color: #0284c7; font-size: 0.95rem;">INR {lodging_cost:,.0f}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center; margin-top: 4px;">
                    <span style="font-size: 0.85rem; color: #64748b; font-weight: 600;">Ideal Stay:</span>
                    <span style="font-weight: 700; color: #334155; font-size: 0.88rem;">{dest['recommended_duration_days']} Days</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"Plan Trip to {dest['destination_name']}", key=f"plan_{dest['destination_id']}", use_container_width=True, type="primary"):
                st.session_state["selected_dest_id"] = dest["destination_id"]
                st.switch_page("pages/2_AI_Trip_Planner.py")

# Call to Action Banner
st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)
with st.container(border=True):
    c_cta1, c_cta2 = st.columns([3, 1.2])
    with c_cta1:
        st.markdown("""
        <div style="padding: 6px 0;">
            <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; margin-bottom: 4px;">
                Ready to plan your complete door-to-door journey?
            </div>
            <div style="font-size: 0.92rem; color: #64748b;">
                Calculate travel distances from your starting city, compare train/flight/bus fares, generate day-by-day schedules, and export PDF travel packs.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with c_cta2:
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        if st.button("🚀 Open AI Trip Planner", type="primary", use_container_width=True):
            st.switch_page("pages/2_AI_Trip_Planner.py")

st.markdown("<div style='height: 36px;'></div>", unsafe_allow_html=True)

# -------------------------------------------------------------
# 5. 3-Step "How TripGenie AI Works"
# -------------------------------------------------------------
st.subheader("🛠️ How TripGenie AI Works")
s1, s2, s3 = st.columns(3)
with s1:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center; padding: 12px 6px;">
            <div style="width: 44px; height: 44px; background: #f0fdfa; color: #0d9488; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; margin-bottom: 12px;">
                1
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.15rem; color: #0f172a; margin-bottom: 6px;">
                Origin & Preferences
            </div>
            <div style="font-size: 0.9rem; color: #64748b; line-height: 1.5;">
                Enter your starting city, domestic or international scope, preferred travel style, budget, and travel interests.
            </div>
        </div>
        """, unsafe_allow_html=True)
with s2:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center; padding: 12px 6px;">
            <div style="width: 44px; height: 44px; background: #e0f2fe; color: #0284c7; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; margin-bottom: 12px;">
                2
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.15rem; color: #0f172a; margin-bottom: 6px;">
                AI Journey Itinerary
            </div>
            <div style="font-size: 0.9rem; color: #64748b; line-height: 1.5;">
                Our engine designs a complete trip plan including outbound departure, hotel check-in, verified attractions, meals, and return journey.
            </div>
        </div>
        """, unsafe_allow_html=True)
with s3:
    with st.container(border=True):
        st.markdown("""
        <div style="text-align: center; padding: 12px 6px;">
            <div style="width: 44px; height: 44px; background: #fef3c7; color: #b45309; border-radius: 12px; display: inline-flex; align-items: center; justify-content: center; font-size: 1.4rem; font-weight: 800; margin-bottom: 12px;">
                3
            </div>
            <div style="font-family: 'Outfit', sans-serif; font-weight: 800; font-size: 1.15rem; color: #0f172a; margin-bottom: 6px;">
                Budget & Document Export
            </div>
            <div style="font-size: 0.9rem; color: #64748b; line-height: 1.5;">
                Examine itemized financial breakdowns with shortfall alerts, check weather, and download your ready-to-travel PDF or CSV document.
            </div>
        </div>
        """, unsafe_allow_html=True)

# Footer
st.markdown("<div style='height: 48px;'></div>", unsafe_allow_html=True)
st.markdown(f"""
<div style="text-align: center; color: #94a3b8; font-size: 0.85rem; border-top: 1px solid #e2e8f0; padding-top: 24px; padding-bottom: 24px;">
    <strong>{APP_NAME}</strong> — {APP_TAGLINE} | Powered by Streamlit, Scikit-learn, Folium & Open-Meteo | Offline-First Architecture
</div>
""", unsafe_allow_html=True)
