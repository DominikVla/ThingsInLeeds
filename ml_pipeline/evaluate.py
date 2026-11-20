"""Evaluate Ollama NL-to-JSON performance against a JSONL test dataset."""

import argparse
import json
import sys
import time
from pathlib import Path

import httpx
from pydantic import ValidationError

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.schemas import VenueFilters

SYSTEM_PROMPT = (
    "Translate the Leeds venue query into JSON matching the VenueFilters schema. "
    "Return only valid JSON."
)


def field_accuracy(expected: dict, actual: dict) -> float:
    keys = set(expected) | set(actual)
    if not keys:
        return 1.0
    matches = sum(1 for key in keys if expected.get(key) == actual.get(key))
    return matches / len(keys)


def evaluate(dataset_path: Path, model: str, ollama_url: str) -> dict:
    valid = 0
    accuracies = []
    latencies = []
    total = 0

    with dataset_path.open(encoding="utf-8") as stream:
        rows = [json.loads(line) for line in stream if line.strip()]

    with httpx.Client(timeout=60) as client:
        for row in rows:
            total += 1
            started = time.perf_counter()
            response = client.post(
                f"{ollama_url.rstrip('/')}/api/generate",
                json={
                    "model": model,
                    "system": SYSTEM_PROMPT,
                    "prompt": row["prompt"],
                    "stream": False,
                    "format": "json",
                },
            )
            response.raise_for_status()
            latencies.append(time.perf_counter() - started)
            try:
                raw = json.loads(response.json()["response"])
                parsed = VenueFilters.model_validate(raw)
                valid += 1
                accuracies.append(field_accuracy(row["expected_json"], parsed.model_dump(mode="json")))
            except (json.JSONDecodeError, KeyError, ValidationError):
                accuracies.append(0.0)

    return {
        "examples": total,
        "json_validity_rate": valid / total if total else 0.0,
        "field_level_accuracy": sum(accuracies) / total if total else 0.0,
        "mean_inference_latency_seconds": (
            sum(latencies) / len(latencies) if latencies else 0.0
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", default="ml_pipeline/test_dataset.jsonl")
    parser.add_argument("--model", default="llama3.2:3b")
    parser.add_argument("--ollama-url", default="http://localhost:11434")
    args = parser.parse_args()
    print(json.dumps(
        evaluate(Path(args.dataset), args.model, args.ollama_url),
        indent=2,
    ))


if __name__ == "__main__":
    main()
