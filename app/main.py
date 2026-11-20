import json
from pathlib import Path
from typing import Any

import httpx
from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db, search_venues
from app.schemas import VenueFilters

app = FastAPI(title="Things in Leeds", version="1.0.0")

SYSTEM_PROMPT = """You translate a Leeds venue search into JSON only.
Use this exact schema:
{
  "venue_types": ["hospitality" | "attraction" | "accommodation"],
  "neighbourhoods": ["string"],
  "max_price_tier": 1 | 2 | 3 | 4 | null,
  "max_budget_gbp": number | null,
  "is_free_entry": boolean | null,
  "categories": ["string"],
  "open_at_time": "HH:MM" | null,
  "vibe_keywords": ["string"]
}
Return no markdown or explanation."""


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    template = Path(__file__).with_name("index.html")
    return template.read_text(encoding="utf-8")


@app.post("/api/translate")
async def translate(query: dict[str, str]) -> VenueFilters:
    text = query.get("query", "").strip()
    if not text:
        raise HTTPException(status_code=400, detail="query is required")

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{settings.ollama_url}/api/generate",
                json={
                    "model": settings.ollama_model,
                    "system": SYSTEM_PROMPT,
                    "prompt": text,
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            payload = response.json()
        data = json.loads(payload["response"])
        return VenueFilters.model_validate(data)
    except (httpx.HTTPError, json.JSONDecodeError, ValidationError, KeyError) as exc:
        raise HTTPException(status_code=502, detail=f"Invalid LLM response: {exc}") from exc


@app.post("/api/search")
async def search(filters: VenueFilters, db: Session = Depends(get_db)) -> dict[str, Any]:
    try:
        results = search_venues(db, filters)
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {exc}") from exc
    return {"filters": filters.model_dump(mode="json"), "count": len(results), "results": results}
