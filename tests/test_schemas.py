from pydantic import ValidationError

from app.schemas import VenueFilters
from ml_pipeline.evaluate import field_accuracy


def test_valid_filter_schema():
    result = VenueFilters.model_validate({
        "venue_types": ["hospitality", "attraction"],
        "neighbourhoods": ["Headingley"],
        "max_price_tier": 2,
        "max_budget_gbp": 25,
        "is_free_entry": True,
        "categories": ["Pub"],
        "open_at_time": "22:30",
        "vibe_keywords": ["lively"],
    })
    assert result.open_at_time.isoformat(timespec="minutes") == "22:30"


def test_filter_schema_rejects_extra_fields():
    try:
        VenueFilters.model_validate({"unknown": "value"})
    except ValidationError:
        return
    raise AssertionError("Unexpected extra field was accepted")


def test_field_accuracy():
    expected = {"venue_types": ["hospitality"], "max_price_tier": 2}
    actual = {"venue_types": ["hospitality"], "max_price_tier": 3}
    assert field_accuracy(expected, actual) == 0.5
