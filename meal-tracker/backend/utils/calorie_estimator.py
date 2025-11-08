from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, Iterable, List, Tuple, Union

DEFAULT_MACROS = {"calories": 220, "protein": 8, "carbs": 20, "fat": 9}
QUANTITY_HINTS = {
    "half": 0.5,
    "quarter": 0.25,
    "double": 2.0,
    "single": 1.0,
}
QUANTITY_PATTERN = re.compile(r"^(?P<quantity>\d+(?:\.\d+)?)\s*(?:x|×)?\s*(?P<name>.*)$")


@dataclass(frozen=True)
class MacroProfile:
    calories: float
    protein: float
    carbs: float
    fat: float


FOOD_LIBRARY: Dict[str, MacroProfile] = {
    "salad": MacroProfile(150, 4, 12, 9),
    "grilled chicken": MacroProfile(250, 35, 0, 11),
    "chicken": MacroProfile(240, 32, 0, 12),
    "rice": MacroProfile(210, 4, 45, 2),
    "brown rice": MacroProfile(195, 4, 41, 2),
    "avocado": MacroProfile(160, 3, 9, 15),
    "smoothie": MacroProfile(190, 6, 32, 4),
    "pasta": MacroProfile(320, 12, 58, 4),
    "whole grain pasta": MacroProfile(300, 13, 54, 4),
    "oatmeal": MacroProfile(180, 6, 30, 4),
    "berries": MacroProfile(85, 1, 21, 0),
    "veggies": MacroProfile(120, 4, 18, 2),
    "steak": MacroProfile(400, 32, 0, 30),
    "tofu": MacroProfile(160, 16, 6, 9),
    "protein shake": MacroProfile(200, 25, 6, 5),
    "yogurt": MacroProfile(120, 12, 14, 3),
    "greek yogurt": MacroProfile(140, 17, 9, 5),
    "eggs": MacroProfile(150, 12, 1, 11),
    "egg": MacroProfile(78, 6, 0, 5),
    "sweet potato": MacroProfile(130, 2, 27, 0),
    "quinoa": MacroProfile(220, 8, 39, 3),
    "lentils": MacroProfile(200, 18, 34, 1),
    "beans": MacroProfile(210, 15, 35, 2),
    "banana": MacroProfile(105, 1, 27, 0),
    "apple": MacroProfile(95, 0, 25, 0),
    "spinach": MacroProfile(40, 5, 4, 0),
}


def _normalized_name(value: str) -> str:
    return value.strip().lower()


def _quantity_from_string(label: str) -> Tuple[str, float]:
    cleaned = label.strip()
    if not cleaned:
        return "", 1.0

    lower = cleaned.lower()
    for hint, factor in QUANTITY_HINTS.items():
        prefix = f"{hint} "
        if lower.startswith(prefix):
            return cleaned[len(hint):].strip(), factor

    match = QUANTITY_PATTERN.match(cleaned)
    if match:
        quantity = float(match.group("quantity"))
        name = match.group("name").strip()
        return (name or cleaned, max(quantity, 0.1))
    return cleaned, 1.0


def _lookup_profile(name: str) -> MacroProfile:
    return FOOD_LIBRARY.get(_normalized_name(name), MacroProfile(**DEFAULT_MACROS))


def _scale_profile(profile: MacroProfile, quantity: float) -> Dict[str, float]:
    return {
        "calories": round(profile.calories * quantity, 1),
        "protein": round(profile.protein * quantity, 1),
        "carbs": round(profile.carbs * quantity, 1),
        "fat": round(profile.fat * quantity, 1),
    }


def normalize_foods(
    foods: Union[Iterable[str], Iterable[Dict[str, Union[str, float]]]]
) -> List[Dict[str, Union[str, float]]]:
    normalized: List[Dict[str, Union[str, float]]] = []
    for item in foods or []:
        if isinstance(item, str):
            name, quantity = _quantity_from_string(item)
            profile = _lookup_profile(name)
            macros = _scale_profile(profile, quantity)
            normalized.append(
                {
                    "name": name or "Unknown food",
                    "calories": macros["calories"],
                    "quantity": quantity,
                    "macros": {k: v for k, v in macros.items() if k != "calories"},
                    "source": "library" if name else "fallback",
                }
            )
        elif isinstance(item, dict):
            name = str(item.get("name", "")).strip()
            quantity = float(item.get("quantity") or item.get("servings") or 1) or 1
            calories = item.get("calories")
            macros = item.get("macros")
            if calories is None or calories == 0:
                profile = _lookup_profile(name)
                scaled = _scale_profile(profile, quantity)
                calories = scaled["calories"]
                macros = macros or {k: v for k, v in scaled.items() if k != "calories"}
            normalized.append(
                {
                    "name": name or "Unknown food",
                    "calories": round(float(calories), 1) if calories is not None else DEFAULT_MACROS["calories"],
                    "quantity": quantity,
                    "macros": macros,
                    "source": item.get("source", "manual"),
                }
            )
    deduped: Dict[str, Dict[str, Union[str, float, Dict]]] = {}
    for entry in normalized:
        key = _normalized_name(str(entry.get("name", "")))
        if not key:
            continue
        if key not in deduped:
            deduped[key] = entry
            continue
        target = deduped[key]
        target["calories"] = round(float(target.get("calories", 0)) + float(entry.get("calories", 0)), 1)
        target["quantity"] = round(float(target.get("quantity", 0)) + float(entry.get("quantity", 0)), 2)
        target_macros = target.get("macros") or {}
        entry_macros = entry.get("macros") or {}
        if target_macros or entry_macros:
            merged = {macro: round(float(target_macros.get(macro, 0)) + float(entry_macros.get(macro, 0)), 1) for macro in ("protein", "carbs", "fat")}
            target["macros"] = merged
    return list(deduped.values())


def estimate_calories(
    foods: Union[Iterable[str], Iterable[Dict[str, Union[str, float]]]]
) -> Tuple[List[Dict[str, Union[str, float]]], float]:
    normalized = normalize_foods(foods)
    total = 0.0
    for entry in normalized:
        calories = entry.get("calories")
        if calories is None:
            calories = DEFAULT_MACROS["calories"]
            entry["calories"] = calories
        total += float(calories)
    return normalized, round(total, 1)
