#!/usr/bin/env python3
"""Upload words from data/*.json to Mochi via API."""

import argparse
import json
import time
from pathlib import Path

import requests

API_BASE = "https://app.mochi.cards/api"
API_KEY = "d7f519d532ec0476408b328d"
TEMPLATE_ID = "Cmf4JjAG"

# level + sublevel -> deck ID
DECK_MAP = {
    ("A2", "beginner"): "cfkDPLZE",
    ("A2", "intermediate"): "cBFdy0dc",
    ("A2", "advance"): "AprtrRc0",
    ("B1", "beginner"): "c8MVe08X",
    ("B1", "intermediate"): "mCjoqzcf",
    ("B1", "advance"): "kssAcVNY",
    ("B2", "beginner"): "qXf4nAev",
    ("B2", "intermediate"): "DNQNMTRD",
    ("B2", "advance"): "67ZWm7hn",
    ("C1", "beginner"): "vVQdh8rp",
    ("C1", "intermediate"): "UaVf30BJ",
    ("C1", "advance"): "pfUhWQa2",
}

# JSON field -> (template field ID, template field name)
FIELD_MAP = {
    "word": ("name", "Word"),
    "part_of_speech": ("39H26Wpc", "Part of speech"),
    "definition": ("C8cx6HFb", "Definition"),
    "example": ("fYg9Kx07", "Example"),
    "translation": ("yeAAPAUQ", "Translation"),
    "collocations": ("igIW8zAx", "Collocations"),
    "synonyms_nuance": ("THTJKPzM", "Synonyms & Nuance"),
    "cloze": ("9sbCiG4l", "Cloze"),
}


def create_card(data: dict) -> dict:
    """Send POST request to create a card via Mochi API."""
    resp = requests.post(
        f"{API_BASE}/cards",
        json=data,
        auth=(API_KEY, ""),
    )
    resp.raise_for_status()
    return resp.json()


def upload_word(word: dict) -> dict:
    """Upload a single word to Mochi."""
    deck_id = DECK_MAP.get((word["level"], word["sublevel"]))
    if not deck_id:
        raise ValueError(f"Unknown deck for {word['level']} / {word['sublevel']}")

    fields = {}
    for json_key, (field_id, _) in FIELD_MAP.items():
        value = word.get(json_key, "")
        if value:
            fields[field_id] = {"id": field_id, "value": value}

    return create_card({
        "content": "",
        "deck-id": deck_id,
        "template-id": TEMPLATE_ID,
        "fields": fields,
    })


def upload_file(filepath: Path, dry_run: bool = False) -> tuple[int, int]:
    """Upload all words from a JSON file. Returns (success, errors)."""
    with open(filepath) as f:
        words = json.load(f)

    success = 0
    errors = 0

    for i, word in enumerate(words):
        label = f"[{i+1}/{len(words)}] {word['word']}"

        if dry_run:
            deck_id = DECK_MAP.get((word["level"], word["sublevel"]))
            print(f"  {label} -> {word['level']}/{word['sublevel']} ({deck_id})")
            success += 1
            continue

        try:
            create_card_result = upload_word(word)
            print(f"  ✓ {label}")
            success += 1
            time.sleep(0.3)  # rate limit
        except requests.HTTPError as e:
            print(f"  ✗ {label}: {e.response.status_code} {e.response.text}")
            errors += 1
        except Exception as e:
            print(f"  ✗ {label}: {e}")
            errors += 1

    return success, errors


def main():
    parser = argparse.ArgumentParser(description="Upload words to Mochi")
    parser.add_argument("files", nargs="+", help="JSON files to upload (e.g. data/a2.json)")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be uploaded without sending")
    args = parser.parse_args()

    total_success = 0
    total_errors = 0

    for filepath in args.files:
        path = Path(filepath)
        if not path.exists():
            print(f"File not found: {filepath}")
            continue

        print(f"\n{'[DRY RUN] ' if args.dry_run else ''}Uploading {path.name}...")
        success, errors = upload_file(path, dry_run=args.dry_run)
        total_success += success
        total_errors += errors

    print(f"\nDone: {total_success} uploaded, {total_errors} errors")


if __name__ == "__main__":
    main()
