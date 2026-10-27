"""Data validation schemas and helper functions using Pydantic."""

from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class DestinationSchema(BaseModel):
    """Schema for a single travel destination with destination-specific pricing."""
    destination_id: str = Field(..., description="Unique alphanumeric identifier")
    destination_name: str = Field(..., min_length=2)
    country: str = Field(..., min_length=2)
    country_code: str = Field(..., min_length=2, max_length=3)
    region: str = Field(..., min_length=2)
    latitude: float = Field(..., ge=-90.0, le=90.0)
    longitude: float = Field(..., ge=-180.0, le=180.0)
    destination_type: str = Field(..., min_length=2)
    interests: str = Field(..., description="Comma-separated interest tags")
    recommended_duration_days: int = Field(..., ge=1, le=30)
    currency: str = Field(default="INR", description="Local currency code (e.g. INR, EUR, JPY, USD)")
    accommodation_budget_per_night: float = Field(default=2500.0, ge=200.0, description="Standard baseline hotel night cost")
    food_budget_per_person_per_day: float = Field(default=800.0, ge=100.0, description="Standard food expense per person per day")
    local_transport_budget_per_day: float = Field(default=400.0, ge=50.0, description="Local intra-city transport cost per day")
    sightseeing_budget_per_person_per_day: float = Field(default=500.0, ge=0.0, description="Standard daily sightseeing budget")
    estimated_daily_budget_inr: float = Field(..., ge=500.0)
    budget_category: str = Field(..., pattern="^(Budget|Moderate|Luxury)$")
    best_season: str = Field(..., min_length=2)
    climate_summary: str = Field(..., min_length=5)
    family_friendly: bool = True
    solo_friendly: bool = True
    accessibility_notes: Optional[str] = "Standard accessibility"
    description: str = Field(..., min_length=20)
    key_attractions: str = Field(..., description="Comma-separated attractions")
    transport_notes: Optional[str] = "Accessible by air, rail, or road"
    image_url: Optional[str] = ""
    price_status: str = Field(default="Estimated", pattern="^(Verified|Estimated|Unavailable)$")
    source_name: str = Field(default="OpenStreetMap / Travel Data Commons")
    source_url: str = Field(default="https://en.wikipedia.org/wiki/Tourism")
    last_verified: str = Field(default="2026-10")

    @field_validator("latitude")
    @classmethod
    def validate_lat(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError(f"Latitude must be between -90 and 90, got {v}")
        return round(v, 4)

    @field_validator("longitude")
    @classmethod
    def validate_lon(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError(f"Longitude must be between -180 and 180, got {v}")
        return round(v, 4)


class AttractionSchema(BaseModel):
    """Schema for individual attractions within a destination."""
    attraction_id: str
    destination_id: str
    destination_name: Optional[str] = ""
    attraction_name: str
    category: str
    typical_duration_hours: float = Field(ge=0.5, le=12.0)
    adult_ticket_price: float = Field(default=50.0, ge=0.0)
    child_ticket_price: float = Field(default=0.0, ge=0.0)
    estimated_ticket_inr: float = Field(default=50.0, ge=0.0)
    currency: str = Field(default="INR")
    price_status: str = Field(default="Estimated", pattern="^(Verified|Estimated|Unavailable)$")
    best_time_of_day: str = Field(pattern="^(Morning|Afternoon|Evening|Flexible)$")
    accessibility: str = "Standard"
    description: str
    source_name: str = Field(default="Official Tourism / Ticket Office")
    source_url: str = Field(default="")
    last_verified: str = Field(default="2026-10")


class BudgetRequestSchema(BaseModel):
    """Schema for travel cost estimation requests."""
    destination_id: str
    starting_location: str = "Delhi"
    num_travelers: int = Field(ge=1, le=50)
    num_adults: Optional[int] = Field(default=None, ge=1, le=50)
    num_children: Optional[int] = Field(default=0, ge=0, le=50)
    num_days: int = Field(ge=1, le=60)
    transport_mode: str
    accommodation_tier: str
    food_tier: str
    local_transport_tier: str
    activities_level: str
    contingency_percent: float = Field(ge=0.0, le=50.0)
    user_target_budget: Optional[float] = None
    personal_vehicle_mileage_kmpl: Optional[float] = Field(default=15.0, ge=5.0, le=50.0)
    personal_vehicle_fuel_price_inr: Optional[float] = Field(default=95.0, ge=50.0, le=250.0)


class RecommendationQuerySchema(BaseModel):
    """Schema for recommendation engine queries."""
    origin_city: Optional[str] = "Delhi"
    travel_scope: str = Field(default="All", pattern="^(All|Domestic|International)$")
    selected_interests: List[str] = Field(default_factory=list)
    travel_group: str = "Solo"
    max_budget_inr: Optional[float] = None
    trip_duration_days: Optional[int] = None
    preferred_season: Optional[str] = None
    travel_month: Optional[str] = None
    travel_style: Optional[str] = "Moderate"
    pace: Optional[str] = "Balanced"
    excluded_destinations: List[str] = Field(default_factory=list)
