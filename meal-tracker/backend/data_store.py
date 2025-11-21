from __future__ import annotations

from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import Dict, List, Optional


@dataclass
class Meal:
    id: int
    foods: List[Dict[str, float]]
    ingredients: List[str]
    calories: float
    points: int
    meal_type: Optional[str]
    mood: Optional[str]
    notes: Optional[str]
    photo: Optional[str]
    calorie_method: str
    calorie_confidence: float
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())


_meals: List[Meal] = []
_user_profile: Dict[str, Optional[float]] = {
    "height": None,
    "weight": None,
    "gender": None,
    "age": None,
    "activity_level": None,
}


def _next_meal_id() -> int:
    return len(_meals) + 1


def record_meal(
    foods: List[Dict[str, float]],
    ingredients: Optional[List[str]],
    calories: float,
    points: int,
    meal_type: Optional[str] = None,
    mood: Optional[str] = None,
    notes: Optional[str] = None,
    photo: Optional[str] = None,
    calorie_method: str = "manual",
    calorie_confidence: float = 0.0,
) -> Dict:
    meal = Meal(
        id=_next_meal_id(),
        foods=foods,
        ingredients=ingredients or [],
        calories=round(calories, 1),
        points=points,
        meal_type=meal_type,
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


def update_profile(
    height: Optional[float],
    weight: Optional[float],
    gender: Optional[str] = None,
    age: Optional[float] = None,
    activity_level: Optional[str] = None,
) -> Dict[str, Optional[float]]:
    if height is not None:
        _user_profile["height"] = height
    if weight is not None:
        _user_profile["weight"] = weight
    if gender is not None:
        _user_profile["gender"] = gender
    if age is not None:
        _user_profile["age"] = age
    if activity_level is not None:
        _user_profile["activity_level"] = activity_level
    return _user_profile
