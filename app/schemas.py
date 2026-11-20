from datetime import time
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field


class VenueType(str, Enum):
    hospitality = "hospitality"
    attraction = "attraction"
    accommodation = "accommodation"


class VenueFilters(BaseModel):
    model_config = ConfigDict(extra="forbid")

    venue_types: list[VenueType] = Field(default_factory=list)
    neighbourhoods: list[str] = Field(default_factory=list)
    max_price_tier: int | None = Field(default=None, ge=1, le=4)
    max_budget_gbp: float | None = Field(default=None, ge=0)
    is_free_entry: bool | None = None
    categories: list[str] = Field(default_factory=list)
    open_at_time: time | None = None
    vibe_keywords: list[str] = Field(default_factory=list)
