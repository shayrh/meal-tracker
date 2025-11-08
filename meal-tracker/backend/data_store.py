from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Meal:
    id: int
    foods: List[Dict[str, float]]
    calories: float
    points: int
    mood: Optional[str]
    notes: Optional[str]
    photo: Optional[str]
    calorie_method: str
    calorie_confidence: float
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


_meals: List[Meal] = []
_user_profile: Dict[str, Optional[float]] = {"height": None, "weight": None}


def _next_meal_id() -> int:
    return len(_meals) + 1


def record_meal(
    foods: List[Dict[str, float]],
    calories: float,
    points: int,
    mood: Optional[str] = None,
    notes: Optional[str] = None,
    photo: Optional[str] = None,
    calorie_method: str = "manual",
    calorie_confidence: float = 0.0,
) -> Dict:
    meal = Meal(
        id=_next_meal_id(),
        foods=foods,
        calories=round(calories, 1),
        points=points,
        mood=mood,
        notes=notes,
        photo=photo,
        calorie_method=calorie_method,
        calorie_confidence=round(calorie_confidence, 2),
    )
    _meals.insert(0, meal)
    return asdict(meal)


def meals() -> List[Dict]:
    return [asdict(meal) for meal in _meals]


def meals_since(days: int) -> List[Dict]:
    cutoff = datetime.utcnow() - timedelta(days=days)
    recent: List[Dict] = []
    for meal in _meals:
        try:
            created_at = datetime.fromisoformat(meal.created_at)
        except ValueError:
            created_at = datetime.utcnow()
        if created_at >= cutoff:
            recent.append(asdict(meal))
    return recent


def meal_count() -> int:
    return len(_meals)


def total_points() -> int:
    return sum(meal.points for meal in _meals)


def user_profile() -> Dict[str, Optional[float]]:
    return _user_profile


def update_profile(height: Optional[float], weight: Optional[float]) -> Dict[str, Optional[float]]:
    if height is not None:
        _user_profile["height"] = height
    if weight is not None:
        _user_profile["weight"] = weight
    return _user_profile
