import json
from pathlib import Path
from typing import Dict, List, Sequence

from .validation import sanitize_text


def load_university_catalog(path: str = "data/universities.json") -> List[dict]:
    data_path = Path(path)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent.parent / data_path
    if not data_path.exists():
        return []
    try:
        with data_path.open("r", encoding="utf-8") as handle:
            raw_catalog = json.load(handle)
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(raw_catalog, list):
        return []

    catalog: List[dict] = []
    for item in raw_catalog:
        if not isinstance(item, dict):
            continue
        name = sanitize_text(str(item.get("name", "")), max_length=160)
        country = sanitize_text(str(item.get("country", "")), max_length=80)
        raw_intakes = item.get("intakes", [])
        if not isinstance(raw_intakes, list):
            continue
        intakes: List[str] = []
        for intake_value in raw_intakes:
            intake = sanitize_text(str(intake_value), max_length=80)
            if intake and intake not in intakes:
                intakes.append(intake)
        if name and country and intakes:
            catalog.append({"name": name, "country": country, "intakes": intakes})
    return catalog


def build_university_lookup(catalog: Sequence[dict]) -> Dict[str, dict]:
    lookup: Dict[str, dict] = {}
    for item in catalog:
        if item["name"] not in lookup:
            lookup[item["name"]] = item
    return lookup
