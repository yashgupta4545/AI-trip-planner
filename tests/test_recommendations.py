"""Unit and integration tests for AI/ML recommendation engine."""

import pytest
from src.data_validation import RecommendationQuerySchema
from src.recommendation_engine import DestinationRecommender


@pytest.fixture(scope="module")
def recommender():
    return DestinationRecommender()


def test_interest_based_recommendation(recommender):
    query = RecommendationQuerySchema(
        travel_scope="Domestic",
        selected_interests=["Palaces", "Forts", "Royal Culture"],
        trip_duration_days=3,
        travel_group="Family"
    )
    recs, notice = recommender.recommend(query, top_n=5)
    assert len(recs) == 5
    top_names = [r["destination_name"] for r in recs]
    # At least one major royal/heritage destination in top recommendations
    assert any(name in ["Jaipur", "Udaipur", "Jodhpur", "Gwalior"] for name in top_names)
    assert recs[0]["match_score"] >= 50
    assert "explanation" in recs[0]


def test_budget_constraint_filtering(recommender):
    # Very strict low budget
    query = RecommendationQuerySchema(
        travel_scope="Domestic",
        selected_interests=["Heritage"],
        max_budget_inr=2000.0,
        trip_duration_days=2
    )
    recs, notice = recommender.recommend(query, top_n=5)
    assert len(recs) > 0
    # All recommended destinations must respect daily budget
    for r in recs:
        assert r["estimated_daily_budget_inr"] <= 2000.0


def test_international_scope_constraint(recommender):
    query = RecommendationQuerySchema(
        travel_scope="International",
        selected_interests=["Art", "Romance", "Museums"],
        trip_duration_days=5
    )
    recs, notice = recommender.recommend(query, top_n=5)
    assert len(recs) == 5
    for r in recs:
        assert not r["is_domestic"], f"Expected international destination, got {r['destination_name']}"


def test_exclusion_constraint(recommender):
    query = RecommendationQuerySchema(
        travel_scope="Domestic",
        selected_interests=["Palaces", "Forts"],
        excluded_destinations=["Jaipur", "Udaipur"]
    )
    recs, notice = recommender.recommend(query, top_n=5)
    top_names = [r["destination_name"] for r in recs]
    assert "Jaipur" not in top_names
    assert "Udaipur" not in top_names


def test_overly_restrictive_budget_fallback(recommender):
    # Unreasonably low budget of ₹200/day
    query = RecommendationQuerySchema(
        travel_scope="Domestic",
        max_budget_inr=200.0
    )
    recs, notice = recommender.recommend(query, top_n=3)
    assert len(recs) == 3
    assert notice is not None
    assert "Notice:" in notice
