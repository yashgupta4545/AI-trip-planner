"""AI/ML Hybrid Recommendation Engine for TripGenie AI.
Combines hard constraints filtering with TF-IDF vectorization, Cosine Similarity,
and multi-factor ranking (budget, duration, travel style, seasonality).
"""

from typing import Dict, List, Optional, Tuple
import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.data_loader import get_all_destinations
from src.data_validation import RecommendationQuerySchema


class DestinationRecommender:
    """Hybrid TF-IDF & Rule-based recommendation engine for travel destinations."""

    def __init__(self, destinations_df: Optional[pd.DataFrame] = None):
        self.df = destinations_df if destinations_df is not None else get_all_destinations()
        self.vectorizer = TfidfVectorizer(
            stop_words="english",
            ngram_range=(1, 2),
            max_features=2500,
            sublinear_tf=True
        )
        self._build_feature_matrix()

    def _build_feature_matrix(self):
        """Construct rich semantic text profiles for each destination and fit TF-IDF."""
        corpus = []
        for _, row in self.df.iterrows():
            text_profile = (
                f"{row.get('destination_name', '')} {row.get('region', '')} {row.get('country', '')}. "
                f"Type: {row.get('destination_type', '')}. "
                f"Interests: {row.get('interests', '')}. "
                f"Attractions: {row.get('key_attractions', '')}. "
                f"Climate: {row.get('climate_summary', '')}. "
                f"Best Season: {row.get('best_season', '')}. "
                f"Budget Category: {row.get('budget_category', '')}. "
                f"{row.get('description', '')}"
            )
            corpus.append(text_profile)

        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)

    def recommend(
        self,
        query: RecommendationQuerySchema,
        top_n: int = 6
    ) -> Tuple[List[Dict], Optional[str]]:
        """Generate ranked destination recommendations with plain-English rationales.
        
        Returns:
            Tuple of (list_of_recommendations, alternative_notice_or_none)
        """
        # Step A: Apply hard constraints
        filtered_df = self.df.copy()

        # Scope constraint
        if query.travel_scope == "Domestic":
            filtered_df = filtered_df[filtered_df["is_domestic"]]
        elif query.travel_scope == "International":
            filtered_df = filtered_df[~filtered_df["is_domestic"]]

        # Exclusions constraint
        if query.excluded_destinations:
            excluded_lower = [e.lower().strip() for e in query.excluded_destinations]
            filtered_df = filtered_df[~filtered_df["destination_name"].str.lower().isin(excluded_lower)]

        # Budget constraint
        alternative_notice = None
        if query.max_budget_inr and query.max_budget_inr > 0:
            budget_filtered = filtered_df[filtered_df["estimated_daily_budget_inr"] <= query.max_budget_inr]
            if budget_filtered.empty:
                # If budget is too restrictive, explain and fall back to the closest affordable options
                min_available = filtered_df["estimated_daily_budget_inr"].min()
                alternative_notice = (
                    f"Notice: No destinations strictly matched your daily budget constraint of INR {query.max_budget_inr:,.0f}. "
                    f"Showing the best value alternatives starting at INR {min_available:,.0f}/day."
                )
            else:
                filtered_df = budget_filtered

        # Empty fallback
        if filtered_df.empty:
            filtered_df = self.df.copy()
            alternative_notice = "Notice: Constraints were too restrictive. Showing top diverse recommendations across all destinations."

        # Step B: Feature Engineering for User Query
        user_query_tokens = []
        if query.selected_interests:
            user_query_tokens.append(" ".join(query.selected_interests))
        if query.travel_style:
            user_query_tokens.append(f"{query.travel_style} travel")
        if query.preferred_season:
            user_query_tokens.append(f"{query.preferred_season} season")
        if query.travel_group:
            user_query_tokens.append(f"{query.travel_group} friendly")
        if query.pace:
            user_query_tokens.append(f"{query.pace} pace")

        query_string = " ".join(user_query_tokens).strip()
        if not query_string:
            query_string = "travel adventure heritage nature beach relaxation"

        # Step C: ML Similarity Calculation
        query_vector = self.vectorizer.transform([query_string])
        filtered_indices = filtered_df.index.tolist()
        sub_matrix = self.tfidf_matrix[filtered_indices]
        sim_scores = cosine_similarity(query_vector, sub_matrix)[0]

        # Step D: Multi-Factor Scoring & Ranking
        scored_records = []
        for idx_pos, df_idx in enumerate(filtered_indices):
            row = filtered_df.loc[df_idx]
            raw_sim = float(sim_scores[idx_pos])

            # Multi-factor weights:
            # 1. ML Interest/Description Similarity (45%)
            score_ml = raw_sim * 0.45

            # 2. Budget Suitability (25%)
            score_budget = 0.20
            if query.max_budget_inr and query.max_budget_inr > 0:
                cost = float(row["estimated_daily_budget_inr"])
                if cost <= query.max_budget_inr:
                    # Closer to user budget without exceeding gives optimal allocation
                    budget_ratio = cost / query.max_budget_inr
                    score_budget = 0.25 * min(1.0, 0.5 + (0.5 * budget_ratio))
                else:
                    overage = (cost - query.max_budget_inr) / query.max_budget_inr
                    score_budget = max(0.0, 0.25 * (1.0 - overage))
            elif query.travel_style:
                if query.travel_style.lower() == row["budget_category"].lower():
                    score_budget = 0.25

            # 3. Duration Suitability (15%)
            score_duration = 0.10
            if query.trip_duration_days and query.trip_duration_days > 0:
                rec_dur = float(row["recommended_duration_days"])
                diff = abs(rec_dur - query.trip_duration_days)
                score_duration = 0.15 * max(0.0, 1.0 - (diff / 10.0))

            # 4. Group / Demographic Suitability (15%)
            score_group = 0.10
            if query.travel_group == "Family" and row.get("family_friendly", True):
                score_group = 0.15
            elif query.travel_group == "Solo" and row.get("solo_friendly", True):
                score_group = 0.15
            else:
                score_group = 0.12

            total_composite_score = score_ml + score_budget + score_duration + score_group
            match_percentage = min(99, max(55, int(total_composite_score * 100)))

            # Plain-English explanation generation based on actual features
            explanation = self._build_explanation(row, query, raw_sim)

            rec_dict = row.to_dict()
            rec_dict["match_score"] = match_percentage
            rec_dict["similarity_score"] = round(raw_sim, 3)
            rec_dict["explanation"] = explanation
            scored_records.append(rec_dict)

        # Sort descending by composite match score
        scored_records.sort(key=lambda x: x["match_score"], reverse=True)
        return scored_records[:top_n], alternative_notice

    def _build_explanation(self, row: pd.Series, query: RecommendationQuerySchema, raw_sim: float) -> str:
        """Create transparent, genuine rationale from verified destination attributes."""
        reasons = []

        # Matched interests
        matched_interests = []
        dest_interests = [i.strip().lower() for i in str(row.get("interests", "")).split(",")]
        for user_int in query.selected_interests:
            if any(user_int.lower() in di for di in dest_interests):
                matched_interests.append(user_int)

        if matched_interests:
            reasons.append(f"matches your interests in {', '.join(matched_interests[:3])}")
        else:
            reasons.append(f"offers premier {row.get('destination_type', 'travel')} experiences")

        # Duration match
        if query.trip_duration_days:
            rec_d = row.get("recommended_duration_days", 3)
            if abs(rec_d - query.trip_duration_days) <= 1:
                reasons.append(f"ideal for a {query.trip_duration_days}-day itinerary")

        # Budget match
        if query.max_budget_inr:
            cost = row.get("estimated_daily_budget_inr", 2500)
            if cost <= query.max_budget_inr:
                reasons.append(f"comfortably fits within your daily budget (INR {cost:,.0f}/day)")

        # Group type match
        if query.travel_group == "Family" and row.get("family_friendly", True):
            reasons.append("has family-friendly attractions and amenities")
        elif query.travel_group == "Solo" and row.get("solo_friendly", True):
            reasons.append("is highly rated for solo explorers")

        explanation_str = "Recommended because it " + ", and ".join(reasons) + "."
        return explanation_str


# Helper factory for fast instantiation
_engine_instance = None

def get_recommendation_engine() -> DestinationRecommender:
    """Return singleton instance of DestinationRecommender."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = DestinationRecommender()
    return _engine_instance
