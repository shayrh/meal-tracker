from __future__ import annotations

import hashlib
from typing import List

SAMPLED_FOODS: List[List[str]] = [
    ["salad", "avocado", "berries"],
    ["grilled chicken", "rice", "veggies"],
    ["tofu", "sweet potato", "greens"],
    ["oatmeal", "yogurt", "berries"],
    ["pasta", "salad"],
]


def detect_foods(photo_reference: str) -> List[str]:
    """
    Placeholder detector that produces deterministic guesses based on the hash of the photo reference.
    """
    if not photo_reference:
        return []
    idx = int(hashlib.sha256(photo_reference.encode("utf-8")).hexdigest(), 16) % len(SAMPLED_FOODS)
    return SAMPLED_FOODS[idx]
