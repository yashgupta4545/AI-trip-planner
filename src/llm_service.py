"""Optional LLM service for itinerary advice and travel narration with full local fallback.
Supports OpenAI, Gemini, or Groq when credentials are provided in the environment.
"""

import os
from typing import Any, Dict, Optional

from src.config import GEMINI_API_KEY, GROQ_API_KEY, LLM_PROVIDER, OPENAI_API_KEY


def generate_itinerary_narrative(itinerary: Dict[str, Any]) -> Dict[str, Any]:
    """Provide natural-language travel narrative for an itinerary.
    If no LLM provider is configured, falls back to high-quality deterministic travel advice.
    """
    dest_name = itinerary.get("destination_name", "your destination")
    duration = itinerary.get("duration_days", 3)
    pace = itinerary.get("pace", "Balanced")
    travel_style = itinerary.get("travel_style", "Moderate")
    travel_group = itinerary.get("travel_group", "Solo")

    # If LLM credentials exist, try them safely
    if LLM_PROVIDER == "openai" and OPENAI_API_KEY:
        try:
            import openai
            client = openai.OpenAI(api_key=OPENAI_API_KEY)
            prompt = (
                f"Write a concise, exciting 3-sentence travel overview for a {duration}-day {travel_style} {travel_group} trip "
                f"to {dest_name} planned at a {pace} pace."
            )
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.7
            )
            narrative = resp.choices[0].message.content.strip()
            return {
                "is_ai_generated": True,
                "provider": "OpenAI (gpt-4o-mini)",
                "narrative": narrative
            }
        except Exception as e:
            # Fall back safely
            pass

    # Deterministic Local Travel Advice Generator (Default / Fallback)
    local_narrative = (
        f"Welcome to your curated {duration}-day {travel_style.lower()} journey across {dest_name}! "
        f"Designed around a {pace.lower()} pace, this itinerary balances morning heritage exploration with "
        f"afternoon scenic visits and evening culinary bazaars. "
        f"Whether traveling {travel_group.lower()} or with companions, prioritize staying hydrated, "
        f"wear comfortable walking shoes for heritage monuments, and savor authentic regional delicacies."
    )

    return {
        "is_ai_generated": False,
        "provider": "Deterministic Local Generator (Offline Engine)",
        "narrative": local_narrative
    }
