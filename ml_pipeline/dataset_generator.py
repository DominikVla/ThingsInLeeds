"""Generate a small instruction dataset for local NL-to-filter fine-tuning."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import VenueFilters

NEIGHBOURHOODS = ["City Centre", "Headingley", "Call Lane", "Hyde Park", "Leeds Dock"]
CATEGORIES = ["Pub", "Cocktail Bar", "Museum", "Gallery", "Budget Hotel", "Live Music"]


def generate() -> list[dict]:
    rows = []
    for venue_type in ("hospitality", "attraction", "accommodation"):
        for neighbourhood in NEIGHBOURHOODS:
            for category in CATEGORIES:
                prompt = (
                    f"Find a {category.lower()} in {neighbourhood.lower()} "
                    f"with an affordable {venue_type} experience"
                )
                filters = VenueFilters(
                    venue_types=[venue_type],
                    neighbourhoods=[neighbourhood],
                    max_price_tier=2,
                    categories=[category],
                )
                rows.append({"prompt": prompt, "expected_json": filters.model_dump(mode="json")})
    return rows


def main() -> None:
    output = Path(__file__).with_name("train_dataset.jsonl")
    with output.open("w", encoding="utf-8") as stream:
        for row in generate():
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"Wrote {len(generate())} examples to {output}")


if __name__ == "__main__":
    main()
