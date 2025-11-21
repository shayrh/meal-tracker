from __future__ import annotations

import hashlib
import re
from typing import Dict, List

from utils.calorie_estimator import FOOD_LIBRARY

SAMPLED_FOODS: List[List[str]] = [
    ["salad", "avocado", "berries"],
    ["grilled chicken", "rice", "veggies"],
    ["tofu", "sweet potato", "greens"],
    ["oatmeal", "yogurt", "berries"],
    ["pasta", "salad"],
]

# Lightweight alias map so we can still hit known foods even if the reference text is abbreviated.
KEYWORD_ALIASES: Dict[str, str] = {
    "veg": "veggies",
    "vegetable": "veggies",
    "vegetables": "veggies",
    "greens": "salad",
    "chickenbreast": "grilled chicken",
    "chicken_breast": "grilled chicken",
    "oats": "oatmeal",
    "yoghurt": "yogurt",
    "shake": "protein shake",
    "smoothies": "smoothie",
}


def _normalized_reference(photo_reference: str) -> str:
    cleaned = photo_reference.lower()
    cleaned = cleaned.split("?", 1)[0]
    cleaned = cleaned.split("#", 1)[0]
    cleaned = cleaned.replace("%20", " ")
    cleaned = re.sub(r"data:image/[^;]+;base64,", "", cleaned)
    cleaned = re.sub(r"[_\-.]+", " ", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    return re.sub(r"\s+", " ", cleaned).strip()


def _keyword_hits(photo_reference: str) -> List[str]:
    normalized = _normalized_reference(photo_reference)
    if not normalized:
        return []

    hits: List[str] = []
    # Prioritize longer food names first (e.g., "brown rice" before "rice") to avoid duplicate fragments.
    for food in sorted(FOOD_LIBRARY.keys(), key=len, reverse=True):
        if food in normalized and not any(food in existing or existing in food for existing in hits):
            hits.append(food)

    for alias, canonical in KEYWORD_ALIASES.items():
        if alias in normalized and canonical not in hits:
            hits.append(canonical)

    return hits


def detect_foods(photo_reference: str) -> List[Dict[str, str]]:
    """
    Attempt to infer foods from a photo reference by mining keywords from the URL/filename.
    Falls back to a deterministic hash-based sample when no hints are present.
    """
    if not photo_reference:
        return []

    keywords = _keyword_hits(photo_reference)
    if keywords:
        return [{"name": keyword, "source": "vision-keyword"} for keyword in keywords]

    idx = int(hashlib.sha256(photo_reference.encode("utf-8")).hexdigest(), 16) % len(SAMPLED_FOODS)
    return [{"name": name, "source": "vision-fallback"} for name in SAMPLED_FOODS[idx]]
