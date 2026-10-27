"""Evaluation script for the TripGenie AI recommendation engine.
Evaluates ranking accuracy, constraint adherence, and recommendation diversity across distinct traveler personas.
"""

import sys
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.data_validation import RecommendationQuerySchema
from src.recommendation_engine import DestinationRecommender


def run_evaluation():
    print("=" * 65)
    print("TripGenie AI - Recommendation Engine Evaluation Suite")
    print("=" * 65)

    engine = DestinationRecommender()

    test_personas = [
        {
            "name": "Persona 1: Heritage Explorer (Domestic, Budget)",
            "query": RecommendationQuerySchema(
                travel_scope="Domestic",
                selected_interests=["Palaces", "Forts", "History", "Architecture"],
                trip_duration_days=3,
                max_budget_inr=3000.0,
                travel_group="Solo",
                travel_style="Budget"
            ),
            "expected_keywords": ["palace", "fort", "heritage", "history"]
        },
        {
            "name": "Persona 2: Luxury International Honeymooners",
            "query": RecommendationQuerySchema(
                travel_scope="International",
                selected_interests=["Beaches", "Romantic", "Luxury", "Islands"],
                trip_duration_days=5,
                max_budget_inr=15000.0,
                travel_group="Couple",
                travel_style="Luxury"
            ),
            "expected_keywords": ["beach", "island", "luxury", "romantic"]
        },
        {
            "name": "Persona 3: Family Himalayan Mountain Vacation",
            "query": RecommendationQuerySchema(
                travel_scope="Domestic",
                selected_interests=["Mountains", "Snow", "Pine Forests", "Waterfalls"],
                trip_duration_days=4,
                max_budget_inr=4000.0,
                travel_group="Family",
                travel_style="Moderate"
            ),
            "expected_keywords": ["hill", "mountain", "himalayan", "snow"]
        },
        {
            "name": "Persona 4: High-Tech Metropolitan Solo Traveler",
            "query": RecommendationQuerySchema(
                travel_scope="All",
                selected_interests=["Futuristic", "High-Tech", "Shopping", "Food"],
                trip_duration_days=4,
                max_budget_inr=9000.0,
                travel_group="Solo",
                travel_style="Moderate"
            ),
            "expected_keywords": ["metropolitan", "futuristic", "tech", "food"]
        }
    ]

    total_tests = len(test_personas)
    passed_tests = 0

    for p in test_personas:
        print(f"\nEvaluating {p['name']}...")
        recs, notice = engine.recommend(p["query"], top_n=5)

        if not recs:
            print("  [FAIL] No recommendations returned.")
            continue

        print(f"  Top Match: {recs[0]['destination_name']} ({recs[0]['country']}) - Match: {recs[0]['match_score']}%")
        print(f"  Rationale: {recs[0]['explanation']}")

        # Verify scope constraint
        scope_ok = True
        if p["query"].travel_scope == "Domestic":
            scope_ok = all(r.get("is_domestic", True) for r in recs)
        elif p["query"].travel_scope == "International":
            scope_ok = all(not r.get("is_domestic", False) for r in recs)

        # Verify diversity: At least 4 distinct destinations
        distinct_names = set(r["destination_name"] for r in recs)
        diversity_ok = len(distinct_names) >= min(4, len(recs))

        # Verify relevance: Top match has >= 50% match score
        relevance_ok = recs[0]["match_score"] >= 50

        if scope_ok and diversity_ok and relevance_ok:
            print(f"  [PASS] Scope Verified: {scope_ok} | Diversity: {len(distinct_names)} unique | Relevance: OK")
            passed_tests += 1
        else:
            print(f"  [FAIL] Scope: {scope_ok}, Diversity: {diversity_ok}, Relevance: {relevance_ok}")

    print("\n" + "=" * 65)
    print(f"Evaluation Results: {passed_tests}/{total_tests} Persona Tests Passed ({(passed_tests/total_tests)*100:.1f}%)")
    print("=" * 65)
    return passed_tests == total_tests


if __name__ == "__main__":
    success = run_evaluation()
    sys.exit(0 if success else 1)
