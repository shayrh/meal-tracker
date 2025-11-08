from __future__ import annotations

from typing import Dict, Iterable, List, Optional, Union

from utils.calorie_estimator import estimate_calories
from utils.image_recognition import detect_foods

FoodInput = Union[str, Dict[str, Union[str, float]]]


def detect_calories(
    foods: Optional[Iterable[FoodInput]] = None,
    photo_reference: Optional[str] = None,
    nutrition_hints: Optional[Iterable[FoodInput]] = None,
) -> Dict:
    """
    Provides a unified way to derive a calorie estimate either from explicit foods,
    inferred foods (photo), or extra hints. Returns metadata that callers can surface.
    """
    method = "manual"
    food_source: List[FoodInput] = _materialize(foods)

    if not food_source and nutrition_hints:
        method = "hint"
        food_source = _materialize(nutrition_hints)

    if not food_source and photo_reference:
        method = "photo"
        food_source = detect_foods(photo_reference)

    if not food_source:
        method = "fallback"
        food_source = []

    foods_with_calories, total_calories = estimate_calories(food_source)
    confidence = _confidence_score(method, foods_with_calories)
    return {
        "foods": foods_with_calories,
        "calories": total_calories,
        "method": method,
        "confidence": confidence,
        "explanation": calorie_explanation(foods_with_calories, total_calories, method, confidence),
    }


def calorie_explanation(foods: List[Dict], calories: float, method: str, confidence: float) -> str:
    if not foods:
        return "No recognizable foods detected; using default calorie estimate."

    parts = [f"Detected via {method} input with {int(confidence * 100)}% confidence."]
    breakdown = ", ".join(
        f"{food['name']} ({int(food['calories'])} kcal)" if food.get("calories") else food["name"]
        for food in foods
    )
    parts.append(f"Breakdown: {breakdown}.")
    parts.append(f"Total estimate: {calories} kcal.")
    return " ".join(parts)


def _confidence_score(method: str, foods: List[Dict]) -> float:
    base = {
        "manual": 0.92,
        "photo": 0.78,
        "hint": 0.68,
        "fallback": 0.5,
    }.get(method, 0.6)
    coverage = (sum(1 for food in foods if food.get("calories")) / len(foods)) if foods else 0
    diversity = len({food.get("name") for food in foods if food.get("name")}) / 10 if foods else 0
    confidence = base + 0.1 * coverage + diversity
    return round(max(0.35, min(confidence, 0.98)), 2)


def _materialize(values: Optional[Iterable[FoodInput]]) -> List[FoodInput]:
    if not values:
        return []
    return list(values)
