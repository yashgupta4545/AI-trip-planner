"""UI/UX Design System & Styling Service for TripGenie AI.
Provides rich, modern styling, glassmorphism, Google Fonts, micro-animations,
and customized Streamlit component themes for an ultra-attractive, premium interface.
"""

import streamlit as st


def apply_custom_theme():
    """Inject premium CSS stylesheet into the active Streamlit page."""
    st.markdown("""
<style>
    /* Google Fonts Import */
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Typography & Background */
    html, body, [class*="css"], .stMarkdown, .stText, p, span, div {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    h1, h2, h3, h4, .hero-title, .brand-title {
        font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif !important;
        letter-spacing: -0.02em;
    }

    /* Subtle luxury mesh gradient background */
    .stApp {
        background: radial-gradient(at 0% 0%, rgba(13, 148, 136, 0.05) 0px, transparent 40%),
                    radial-gradient(at 100% 0%, rgba(2, 132, 199, 0.06) 0px, transparent 40%),
                    radial-gradient(at 50% 100%, rgba(245, 158, 11, 0.03) 0px, transparent 40%),
                    #f8fafc;
    }

    /* Sidebar Luxury Styling */
    section[data-testid="stSidebar"] {
        background: #ffffff !important;
        border-right: 1px solid #e2e8f0;
        box-shadow: 4px 0 20px rgba(0, 0, 0, 0.02);
    }

    section[data-testid="stSidebar"] .block-container {
        padding-top: 2rem;
    }

    /* Sidebar Navigation Links */
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        border-radius: 10px !important;
        padding: 8px 14px !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: #334155 !important;
        margin-bottom: 4px !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover {
        background: rgba(13, 148, 136, 0.08) !important;
        color: #0d9488 !important;
        transform: translateX(4px);
    }

    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"] {
        background: linear-gradient(135deg, rgba(13, 148, 136, 0.15), rgba(2, 132, 199, 0.15)) !important;
        color: #0f766e !important;
        font-weight: 700 !important;
        border-left: 3.5px solid #0d9488 !important;
    }

    /* -------------------------------------------------------------
       Customized Sidebar Navigation Labels & Icons
       1. 🏠 Home
       2. 🌍 Explore Destinations
       3. ✨ AI Trip Planner
       4. 💰 Travel Budget
       5. 🧳 My Trips
       6. 🌤️ Weather & Maps
       7. ℹ️ About TripGenie
       ------------------------------------------------------------- */
    /* -------------------------------------------------------------
       Customized Sidebar Navigation Labels & Icons
       1. 🏠 Home
       2. 🌍 Explore Destinations
       3. ✨ AI Trip Planner
       4. 💰 Travel Budget
       5. 🧳 My Trips
       6. 🌤️ Weather & Maps
       7. ℹ️ About TripGenie
       ------------------------------------------------------------- */
    /* Hide the default page text and intermediate spans */
    [data-testid="stSidebarNav"] a span,
    [data-testid="stSidebarNav"] a p,
    section[data-testid="stSidebar"] a span,
    section[data-testid="stSidebar"] a p {
        display: none !important;
        visibility: hidden !important;
        font-size: 0 !important;
        line-height: 0 !important;
    }

    [data-testid="stSidebarNav"] a,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a {
        display: flex !important;
        align-items: center !important;
        justify-content: flex-start !important;
        text-align: left !important;
        padding: 9px 12px !important;
        margin-bottom: 4px !important;
        border-radius: 10px !important;
        text-decoration: none !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    /* Base styling for customized anchor label */
    [data-testid="stSidebarNav"] a::after,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a::after {
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.90rem !important;
        font-weight: 600 !important;
        line-height: 1.4 !important;
        display: inline-block !important;
        color: #334155 !important;
        letter-spacing: -0.01em !important;
        white-space: nowrap !important;
        text-align: left !important;
        transition: color 0.2s ease, transform 0.2s ease !important;
        visibility: visible !important;
    }

    [data-testid="stSidebarNav"] a:hover::after,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a:hover::after {
        color: #0d9488 !important;
    }

    [data-testid="stSidebarNav"] a[aria-current="page"]::after,
    section[data-testid="stSidebar"] [data-testid="stSidebarNav"] a[aria-current="page"]::after {
        color: #0f766e !important;
        font-weight: 700 !important;
    }

    /* 1. 🏠 Home */
    [data-testid="stSidebarNav"] a[href$="/"]::after,
    [data-testid="stSidebarNav"] a:not([href*="_"]):not([href*="About"])::after {
        content: "🏠  Home" !important;
    }

    /* 2. 🌍 Explore Destinations */
    [data-testid="stSidebarNav"] a[href*="Explore_Destinations"]::after {
        content: "🌍  Explore Destinations" !important;
    }

    /* 3. ✨ AI Trip Planner */
    [data-testid="stSidebarNav"] a[href*="AI_Trip_Planner"]::after {
        content: "✨  AI Trip Planner" !important;
    }

    /* 4. 💰 Travel Budget */
    [data-testid="stSidebarNav"] a[href*="Budget_Calculator"]::after {
        content: "💰  Travel Budget" !important;
    }

    /* 5. 🧳 My Trips */
    [data-testid="stSidebarNav"] a[href*="My_Trips"]::after {
        content: "🧳  My Trips" !important;
    }

    /* 6. 🌤️ Weather & Maps */
    [data-testid="stSidebarNav"] a[href*="Weather_and_Maps"]::after {
        content: "🌤️  Weather & Maps" !important;
    }

    /* 7. ℹ️ About TripGenie */
    [data-testid="stSidebarNav"] a[href*="About"]::after {
        content: "ℹ️  About TripGenie" !important;
    }

    /* Hero Banner - Ambient Gradient Mesh with Glassmorphic Accents */
    .hero-container {
        position: relative !important;
        overflow: hidden !important;
        background: linear-gradient(135deg, #091e2b 0%, #0d3b43 30%, #0f766e 70%, #042f2e 100%) !important;
        padding: 50px 44px !important;
        border-radius: 24px !important;
        color: white !important;
        margin-bottom: 34px !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        box-shadow: 0 20px 40px -10px rgba(13, 148, 136, 0.28), 0 1px 3px rgba(0,0,0,0.1) !important;
    }

    .hero-container::before {
        content: "";
        position: absolute;
        top: -60px;
        right: -60px;
        width: 320px;
        height: 320px;
        background: radial-gradient(circle, rgba(2, 132, 199, 0.35) 0%, rgba(13, 148, 136, 0) 70%);
        border-radius: 50%;
        filter: blur(40px);
        pointer-events: none;
    }

    .hero-container::after {
        content: "";
        position: absolute;
        bottom: -40px;
        left: 20%;
        width: 260px;
        height: 260px;
        background: radial-gradient(circle, rgba(245, 158, 11, 0.2) 0%, rgba(13, 148, 136, 0) 70%);
        border-radius: 50%;
        filter: blur(50px);
        pointer-events: none;
    }

    /* Hero Action Buttons */
    .hero-action-row {
        display: flex;
        flex-wrap: wrap;
        gap: 16px;
        margin-top: 26px;
        align-items: center;
        position: relative;
        z-index: 5;
    }

    .hero-btn-primary {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 13px 28px !important;
        border-radius: 12px !important;
        text-decoration: none !important;
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .hero-btn-primary:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(16, 185, 129, 0.65) !important;
        filter: brightness(1.08) !important;
        color: #ffffff !important;
        text-decoration: none !important;
    }

    .hero-btn-secondary {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        gap: 8px !important;
        background: rgba(255, 255, 255, 0.14) !important;
        backdrop-filter: blur(14px) !important;
        -webkit-backdrop-filter: blur(14px) !important;
        color: #ffffff !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 13px 28px !important;
        border-radius: 12px !important;
        text-decoration: none !important;
        border: 1.5px solid rgba(255, 255, 255, 0.45) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .hero-btn-secondary:hover {
        background: rgba(255, 255, 255, 0.26) !important;
        border-color: rgba(255, 255, 255, 0.85) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(0, 0, 0, 0.25) !important;
        color: #ffffff !important;
        text-decoration: none !important;
    }

    .hero-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.25);
        backdrop-filter: blur(12px);
        padding: 6px 16px;
        border-radius: 50px;
        font-size: 0.84rem;
        font-weight: 700;
        color: #f0fdfa;
        margin-bottom: 16px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }

    .hero-title {
        font-size: 2.85rem;
        font-weight: 900;
        letter-spacing: -0.03em;
        line-height: 1.12;
        margin-bottom: 10px;
        color: #ffffff;
    }

    .hero-gradient-text {
        background: linear-gradient(135deg, #a7f3d0 0%, #38bdf8 50%, #fef08a 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .hero-subtitle {
        font-size: 1.25rem;
        color: #ccfbf1;
        font-weight: 400;
        margin-bottom: 22px;
        max-width: 720px;
        line-height: 1.45;
    }

    .hero-desc {
        max-width: 680px;
        font-size: 0.98rem;
        line-height: 1.6;
        color: rgba(240, 253, 250, 0.92);
        margin-bottom: 24px;
    }

    .hero-chips-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-top: 18px;
    }

    .hero-chip {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: rgba(255, 255, 255, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(8px);
        padding: 7px 16px;
        border-radius: 30px;
        font-size: 0.85rem;
        font-weight: 600;
        color: #ffffff;
        text-decoration: none;
        transition: all 0.2s ease;
    }

    .hero-chip:hover {
        background: rgba(255, 255, 255, 0.22);
        transform: translateY(-2px);
        color: #ffffff;
    }

    /* Stat Cards - Modern Luxury Floating Blocks */
    .stat-card-luxury {
        background: #ffffff;
        border-radius: 18px;
        padding: 24px 20px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 16px -2px rgba(15, 23, 42, 0.04), 0 2px 4px rgba(0, 0, 0, 0.02);
        text-align: center;
        position: relative;
        overflow: hidden;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .stat-card-luxury::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #0d9488, #0284c7);
        border-radius: 18px 18px 0 0;
        opacity: 0.85;
    }

    .stat-card-luxury:hover {
        transform: translateY(-5px);
        box-shadow: 0 14px 28px -4px rgba(13, 148, 136, 0.16);
        border-color: #5eead4;
    }

    .stat-icon-wrap {
        width: 44px;
        height: 44px;
        border-radius: 12px;
        background: #f0fdfa;
        color: #0d9488;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.35rem;
        margin-bottom: 12px;
        box-shadow: inset 0 0 0 1px rgba(13, 148, 136, 0.15);
    }

    .stat-number-luxury {
        font-family: 'Outfit', sans-serif !important;
        font-size: 2.3rem;
        font-weight: 800;
        line-height: 1.05;
        background: linear-gradient(135deg, #0f766e 0%, #0284c7 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .stat-label-luxury {
        font-size: 0.84rem;
        color: #64748b;
        font-weight: 700;
        margin-top: 6px;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    /* Streamlit Metric Overrides */
    div[data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 16px 18px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }

    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }

    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        font-family: 'Outfit', sans-serif !important;
        font-size: 1.85rem !important;
        font-weight: 800 !important;
        color: #0f172a !important;
    }

    /* Primary & Secondary Buttons */
    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #0d9488 0%, #0284c7 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 10px 24px !important;
        font-weight: 700 !important;
        font-size: 0.95rem !important;
        letter-spacing: -0.01em !important;
        box-shadow: 0 4px 14px 0 rgba(13, 148, 136, 0.35) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
    }

    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 22px rgba(13, 148, 136, 0.45) !important;
        filter: brightness(1.05);
    }

    div.stButton > button[kind="secondary"] {
        background: #ffffff !important;
        border: 1px solid #cbd5e1 !important;
        color: #334155 !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.2s ease !important;
    }

    div.stButton > button[kind="secondary"]:hover {
        border-color: #0d9488 !important;
        color: #0d9488 !important;
        background: #f0fdfa !important;
    }

    /* Hero Action Buttons (Prominent Primary & Frosted Secondary inside Hero Section) */
    .st-key-hero_section div.stButton > button[kind="primary"],
    div[data-testid="stVerticalBlock"]:has(> div.st-key-hero_btn_plan) button,
    .st-key-hero_btn_plan button {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 26px !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        box-shadow: 0 4px 16px rgba(16, 185, 129, 0.45) !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .st-key-hero_section div.stButton > button[kind="primary"]:hover,
    .st-key-hero_btn_plan button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 24px rgba(16, 185, 129, 0.65) !important;
        filter: brightness(1.08) !important;
    }

    .st-key-hero_section div.stButton > button[kind="secondary"],
    div[data-testid="stVerticalBlock"]:has(> div.st-key-hero_btn_explore) button,
    .st-key-hero_btn_explore button {
        background: rgba(255, 255, 255, 0.15) !important;
        backdrop-filter: blur(12px) !important;
        color: #ffffff !important;
        border: 1.5px solid rgba(255, 255, 255, 0.45) !important;
        border-radius: 12px !important;
        padding: 12px 26px !important;
        font-weight: 700 !important;
        font-size: 1.02rem !important;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
        cursor: pointer !important;
    }

    .st-key-hero_section div.stButton > button[kind="secondary"]:hover,
    .st-key-hero_btn_explore button:hover {
        background: rgba(255, 255, 255, 0.28) !important;
        border-color: rgba(255, 255, 255, 0.85) !important;
        color: #ffffff !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.2) !important;
    }

    /* Container Borders */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff;
        box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.03);
        transition: border-color 0.2s ease, box-shadow 0.2s ease;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: #cbd5e1;
    }

    /* Badges */
    .badge-pill {
        display: inline-flex;
        align-items: center;
        gap: 4px;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.02em;
    }

    .badge-domestic {
        background: #ccfbf1;
        color: #0f766e;
        border: 1px solid #99f6e4;
    }

    .badge-intl {
        background: #e0f2fe;
        color: #0369a1;
        border: 1px solid #bae6fd;
    }

    .badge-verified {
        background: #dcfce7;
        color: #15803d;
        border: 1px solid #bbf7d0;
    }

    .badge-estimated {
        background: #fef3c7;
        color: #b45309;
        border: 1px solid #fde68a;
    }

    /* Tabs Styling */
    div[data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 4px;
    }

    div[data-baseweb="tab"] {
        border-radius: 10px 10px 0 0 !important;
        font-weight: 700 !important;
        font-size: 0.94rem !important;
        padding: 8px 18px !important;
        color: #64748b !important;
    }

    div[data-baseweb="tab"][aria-selected="true"] {
        background: #f0fdfa !important;
        color: #0f766e !important;
        border-bottom: 3px solid #0d9488 !important;
    }

    /* Expanders */
    div[data-testid="stExpander"] {
        border-radius: 14px !important;
        border: 1px solid #e2e8f0 !important;
        background: #ffffff;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }
</style>
""", unsafe_allow_html=True)


def render_sidebar_brand():
    """Render attractive branding header in the sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="padding: 10px 4px 18px 4px; border-bottom: 1px solid #e2e8f0; margin-bottom: 18px;">
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="width: 38px; height: 38px; border-radius: 10px; background: linear-gradient(135deg, #0d9488, #0284c7); display: flex; align-items: center; justify-content: center; font-size: 1.3rem; box-shadow: 0 4px 10px rgba(13, 148, 136, 0.35);">
                    ✈️
                </div>
                <div>
                    <div style="font-family: 'Outfit', sans-serif; font-size: 1.25rem; font-weight: 800; color: #0f172a; line-height: 1.1;">
                        TripGenie <span style="color: #0d9488;">AI</span>
                    </div>
                    <div style="font-size: 0.75rem; color: #64748b; font-weight: 600;">
                        Smart Travel & Budget v1.0
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
