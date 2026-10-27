"""Configuration constants and application settings for TripGenie AI."""

import os
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DESTINATIONS_FILE = DATA_DIR / "destinations.csv"
ATTRACTIONS_FILE = DATA_DIR / "attractions.csv"
BUDGET_ESTIMATES_FILE = DATA_DIR / "budget_estimates.csv"
DATABASE_FILE = BASE_DIR / "trips.db"

# App Branding
APP_NAME = "TripGenie AI"
APP_TAGLINE = "Your Journey. Your Budget. Your Adventure."
APP_VERSION = "1.0.0"

# Design Tokens (Hex Color Codes)
COLOR_PRIMARY = "#0d9488"       # Teal
COLOR_PRIMARY_DARK = "#115e59"  # Deep Teal
COLOR_PRIMARY_LIGHT = "#ccfbf1" # Soft Mint
COLOR_SECONDARY = "#0284c7"     # Ocean Blue
COLOR_ACCENT = "#f59e0b"        # Warm Amber / Gold
COLOR_BG = "#f8fafc"            # Neutral Light Background
COLOR_CARD_BG = "#ffffff"       # Card White
COLOR_TEXT_MAIN = "#0f172a"     # Slate Navy
COLOR_TEXT_MUTED = "#64748b"    # Muted Slate
COLOR_BORDER = "#e2e8f0"        # Light Slate Border
COLOR_SUCCESS = "#10b981"       # Emerald Green
COLOR_WARNING = "#f59e0b"       # Amber
COLOR_DANGER = "#ef4444"        # Crimson

# Travel Taxonomies
TRAVEL_GROUP_TYPES = ["Solo", "Couple", "Family", "Friends / Group"]
TRAVEL_STYLES = [
    "Budget",
    "Moderate",
    "Luxury",
    "Backpacking",
    "Adventure",
    "Heritage & Culture",
    "Relaxation & Beach",
    "Nature & Wildlife",
    "Food & Nightlife",
]
TRIP_PACES = [
    ("Relaxed", "1-2 activities/day with ample leisure time"),
    ("Balanced", "2-3 activities/day with pleasant breaks"),
    ("Packed", "3-4 activities/day maximizing sightseeing"),
]
BUDGET_TIERS = ["Budget", "Moderate", "Luxury"]
ACCOMMODATION_TIERS = [
    "Hostel / Backpacker Pod",
    "Budget Hotel / Guesthouse",
    "Mid-range 3-Star Hotel",
    "Boutique / 4-Star Hotel",
    "5-Star Luxury Resort",
]
TRANSPORT_MODES = [
    "Flight",
    "Train (Express / AC)",
    "Intercity Bus",
    "Self-drive / Rental Car",
    "Local Public Transit",
]

# Weather Settings
OPEN_METEO_BASE_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_CACHE_TTL_SECONDS = 3600

# LLM Providers (Optional)
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").lower()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Default Currency
DEFAULT_CURRENCY = "INR"
CURRENCY_SYMBOL = "₹"
