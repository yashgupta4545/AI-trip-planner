"""Data loader service for TripGenie AI.
Loads, caches, filters, and searches destination, attraction, and budget datasets.
"""

from typing import Dict, List, Optional
import pandas as pd
from src.config import DESTINATIONS_FILE, ATTRACTIONS_FILE, BUDGET_ESTIMATES_FILE


# Optional Streamlit caching decorator wrapper
try:
    import streamlit as st
    cache_decorator = st.cache_data
except ImportError:
    def cache_decorator(func):
        return func


@cache_decorator
def load_destinations_raw() -> pd.DataFrame:
    """Load destinations CSV into DataFrame with standardized data types."""
    if not DESTINATIONS_FILE.exists():
        raise FileNotFoundError(f"Destinations file not found at {DESTINATIONS_FILE}")

    df = pd.read_csv(DESTINATIONS_FILE)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df["recommended_duration_days"] = pd.to_numeric(df["recommended_duration_days"], errors="coerce").fillna(3).astype(int)
    df["estimated_daily_budget_inr"] = pd.to_numeric(df["estimated_daily_budget_inr"], errors="coerce").fillna(2500.0)
    df["accommodation_budget_per_night"] = pd.to_numeric(df.get("accommodation_budget_per_night", 2500.0), errors="coerce").fillna(2500.0)
    df["food_budget_per_person_per_day"] = pd.to_numeric(df.get("food_budget_per_person_per_day", 800.0), errors="coerce").fillna(800.0)
    df["local_transport_budget_per_day"] = pd.to_numeric(df.get("local_transport_budget_per_day", 400.0), errors="coerce").fillna(400.0)
    df["sightseeing_budget_per_person_per_day"] = pd.to_numeric(df.get("sightseeing_budget_per_person_per_day", 400.0), errors="coerce").fillna(400.0)
    df["currency"] = df.get("currency", "INR").fillna("INR").astype(str)
    df["price_status"] = df.get("price_status", "Estimated").fillna("Estimated").astype(str)
    df["family_friendly"] = df["family_friendly"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["solo_friendly"] = df["solo_friendly"].astype(str).str.lower().isin(["true", "1", "yes"])
    df["is_domestic"] = df["country"].str.strip().str.lower() == "india"
    return df


@cache_decorator
def load_attractions_raw() -> pd.DataFrame:
    """Load attractions CSV into DataFrame."""
    if not ATTRACTIONS_FILE.exists():
        raise FileNotFoundError(f"Attractions file not found at {ATTRACTIONS_FILE}")

    df = pd.read_csv(ATTRACTIONS_FILE)
    df["typical_duration_hours"] = pd.to_numeric(df["typical_duration_hours"], errors="coerce").fillna(2.0)
    df["estimated_ticket_inr"] = pd.to_numeric(df["estimated_ticket_inr"], errors="coerce").fillna(0.0)
    df["adult_ticket_price"] = pd.to_numeric(df.get("adult_ticket_price", df["estimated_ticket_inr"]), errors="coerce").fillna(df["estimated_ticket_inr"])
    df["child_ticket_price"] = pd.to_numeric(df.get("child_ticket_price", 0.0), errors="coerce").fillna(0.0)
    df["currency"] = df.get("currency", "INR").fillna("INR").astype(str)
    df["price_status"] = df.get("price_status", "Estimated").fillna("Estimated").astype(str)
    return df


@cache_decorator
def load_budget_estimates_raw() -> pd.DataFrame:
    """Load baseline budget multipliers and tier estimates."""
    if not BUDGET_ESTIMATES_FILE.exists():
        raise FileNotFoundError(f"Budget estimates file not found at {BUDGET_ESTIMATES_FILE}")

    df = pd.read_csv(BUDGET_ESTIMATES_FILE)
    df["base_daily_inr"] = pd.to_numeric(df["base_daily_inr"], errors="coerce")
    return df


def get_all_destinations() -> pd.DataFrame:
    """Return all destinations."""
    return load_destinations_raw().copy()


def get_all_attractions() -> pd.DataFrame:
    """Return all attractions."""
    return load_attractions_raw().copy()


def get_budget_estimates() -> pd.DataFrame:
    """Return baseline budget tier estimates."""
    return load_budget_estimates_raw().copy()


def get_destination_by_id(destination_id: str) -> Optional[Dict]:
    """Retrieve full destination details by ID."""
    df = load_destinations_raw()
    match = df[df["destination_id"] == destination_id]
    if match.empty:
        return None
    return match.iloc[0].to_dict()


def get_attractions_for_destination(destination_id: str) -> List[Dict]:
    """Retrieve attractions mapped to a specific destination."""
    df = load_attractions_raw()
    matches = df[df["destination_id"] == destination_id]
    return matches.to_dict(orient="records")


def search_destinations(
    query: str = "",
    scope: str = "All",
    country: Optional[str] = None,
    destination_type: Optional[str] = None,
    budget_category: Optional[str] = None,
    max_budget: Optional[float] = None,
    selected_interest: Optional[str] = None,
) -> pd.DataFrame:
    """Search and filter destinations across multiple criteria."""
    df = load_destinations_raw().copy()

    # Scope filter
    if scope == "Domestic":
        df = df[df["is_domestic"]]
    elif scope == "International":
        df = df[~df["is_domestic"]]

    # Country filter
    if country and country != "All":
        df = df[df["country"].str.lower() == country.lower()]

    # Destination type filter
    if destination_type and destination_type != "All":
        df = df[df["destination_type"].str.contains(destination_type, case=False, na=False)]

    # Budget category filter
    if budget_category and budget_category != "All":
        df = df[df["budget_category"].str.lower() == budget_category.lower()]

    # Max daily budget filter
    if max_budget and max_budget > 0:
        df = df[df["estimated_daily_budget_inr"] <= max_budget]

    # Specific interest filter
    if selected_interest and selected_interest != "All":
        df = df[df["interests"].str.contains(selected_interest, case=False, na=False)]

    # Free text search across name, region, country, description, and attractions
    if query and query.strip():
        q = query.strip().lower()
        text_match = (
            df["destination_name"].str.lower().str.contains(q, na=False)
            | df["country"].str.lower().str.contains(q, na=False)
            | df["region"].str.lower().str.contains(q, na=False)
            | df["interests"].str.lower().str.contains(q, na=False)
            | df["description"].str.lower().str.contains(q, na=False)
            | df["key_attractions"].str.lower().str.contains(q, na=False)
        )
        df = df[text_match]

    return df


def get_distinct_countries(scope: str = "All") -> List[str]:
    """Return sorted list of distinct countries."""
    df = load_destinations_raw()
    if scope == "Domestic":
        return ["India"]
    elif scope == "International":
        df = df[~df["is_domestic"]]
    countries = sorted(df["country"].dropna().unique().tolist())
    return countries


def get_distinct_interests() -> List[str]:
    """Extract individual unique interest tags."""
    df = load_destinations_raw()
    all_interests = set()
    for item in df["interests"].dropna():
        tags = [t.strip() for t in str(item).split(",")]
        all_interests.update([t for t in tags if len(t) > 2])
    return sorted(list(all_interests))


def get_distinct_destination_types() -> List[str]:
    """Return unique destination types."""
    df = load_destinations_raw()
    types = sorted(df["destination_type"].dropna().unique().tolist())
    return types


def get_dataset_summary() -> Dict:
    """Return aggregate statistics about the dataset."""
    df = load_destinations_raw()
    attrs = load_attractions_raw()
    domestic_count = int(df["is_domestic"].sum())
    intl_count = int((~df["is_domestic"]).sum())
    return {
        "total_destinations": len(df),
        "domestic_destinations": domestic_count,
        "international_destinations": intl_count,
        "total_attractions": len(attrs),
        "total_countries": int(df["country"].nunique()),
        "average_duration_days": round(float(df["recommended_duration_days"].mean()), 1),
        "min_daily_budget_inr": float(df["estimated_daily_budget_inr"].min()),
        "max_daily_budget_inr": float(df["estimated_daily_budget_inr"].max()),
    }
