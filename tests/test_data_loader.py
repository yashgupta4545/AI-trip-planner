"""Unit and integration tests for data loading and filtering."""

import pytest
import pandas as pd
from src.data_loader import (
    get_all_destinations,
    get_all_attractions,
    get_destination_by_id,
    get_attractions_for_destination,
    search_destinations,
    get_dataset_summary,
    get_distinct_countries,
    get_distinct_interests
)


def test_destinations_loading():
    df = get_all_destinations()
    assert isinstance(df, pd.DataFrame)
    assert len(df) >= 300, f"Expected at least 300 destinations, got {len(df)}"
    required_cols = [
        "destination_id", "destination_name", "country", "region",
        "latitude", "longitude", "destination_type", "interests",
        "recommended_duration_days", "estimated_daily_budget_inr"
    ]
    for col in required_cols:
        assert col in df.columns, f"Missing required column {col}"


def test_no_duplicate_destination_ids():
    df = get_all_destinations()
    duplicates = df[df.duplicated(subset=["destination_id"], keep=False)]
    assert duplicates.empty, f"Found duplicate destination IDs: {duplicates['destination_id'].tolist()}"


def test_valid_coordinates():
    df = get_all_destinations()
    invalid_lats = df[(df["latitude"] < -90.0) | (df["latitude"] > 90.0)]
    invalid_lons = df[(df["longitude"] < -180.0) | (df["longitude"] > 180.0)]
    assert invalid_lats.empty, f"Found invalid latitudes: {len(invalid_lats)}"
    assert invalid_lons.empty, f"Found invalid longitudes: {len(invalid_lons)}"


def test_domestic_and_international_filtering():
    df = get_all_destinations()
    domestic = df[df["is_domestic"]]
    international = df[~df["is_domestic"]]

    assert len(domestic) >= 150, f"Expected at least 150 domestic destinations, got {len(domestic)}"
    assert len(international) >= 150, f"Expected at least 150 international destinations, got {len(international)}"
    assert all(domestic["country"] == "India")
    assert all(international["country"] != "India")


def test_search_functionality():
    # Search for known iconic landmark
    res_taj = search_destinations(query="Taj Mahal")
    assert not res_taj.empty
    assert "Agra" in res_taj["destination_name"].values

    # Search with scope
    res_intl = search_destinations(scope="International")
    assert all(~res_intl["is_domestic"])

    # Search with budget cap
    res_budget = search_destinations(max_budget=2000.0)
    assert not res_budget.empty
    assert all(res_budget["estimated_daily_budget_inr"] <= 2000.0)


def test_attractions_mapping():
    attrs = get_all_attractions()
    assert len(attrs) >= 600, f"Expected >= 600 attractions, got {len(attrs)}"

    # Check attractions for Jaipur
    jaipur_attrs = get_attractions_for_destination("IND_JAI_003")
    assert len(jaipur_attrs) >= 3
    assert any("Amber Fort" in a["attraction_name"] or "Hawa Mahal" in a["attraction_name"] for a in jaipur_attrs)
