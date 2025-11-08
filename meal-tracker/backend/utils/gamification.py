from __future__ import annotations

from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Dict, Iterable, List, Optional


def calculate_points(calories: float, foods: Iterable[Dict[str, float]]) -> int:
    base = max(5, 60 - int(calories // 12))
    labels = [item.get("name", "").lower() for item in foods]
    plant_bonus = 5 if any("salad" in label or "vegg" in label for label in labels) else 0
    protein_bonus = 5 if any(token in label for label in labels for token in ["chicken", "tofu", "egg", "yogurt"]) else 0
    variety_bonus = min(10, max(0, len({label for label in labels if label}) - 1) * 2)
    balance_bonus = 8 if 350 <= calories <= 650 else 0
    indulge_penalty = -5 if calories > 900 else 0
    total = base + plant_bonus + protein_bonus + variety_bonus + balance_bonus + indulge_penalty
    return max(5, total)


def _parse_date(date_str: str) -> datetime:
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return datetime.utcnow()


def summarize_achievements(meals: List[Dict], weekly: Optional[Dict] = None) -> List[Dict]:
    weekly = weekly or weekly_summary(meals)
    streaks = streak_report(meals)
    variety = _weekly_variety(meals)
    achievements = [
        {
            "id": "first-log",
            "label": "First Meal Logged",
            "achieved": len(meals) > 0,
            "details": "Unlocked as soon as you record your first meal.",
            "progress": f"{1 if len(meals) else 0}/1",
        },
        {
            "id": "weekly-habit",
            "label": "3-Day Streak",
            "achieved": _longest_streak(meals) >= 3,
            "details": "Log meals three days in a row to prove your consistency.",
            "progress": f"{min(streaks['longest'], 3)}/3",
        },
        {
            "id": "weekly-hero",
            "label": "Weekly Hero",
            "achieved": weekly["count"] >= 5,
            "details": "Capture five meals this week to stay mindful.",
            "progress": f"{min(weekly['count'], 5)}/5",
        },
        {
            "id": "balanced-week",
            "label": "Balanced Week",
            "achieved": 350 <= weekly["averageCalories"] <= 700 and weekly["count"] >= 3,
            "details": "Keep your weekly average calories in the healthy sweet spot.",
            "progress": f"{int(weekly['averageCalories'])} avg kcal",
        },
        {
            "id": "colorful-plate",
            "label": "Colorful Plate",
            "achieved": variety >= 5,
            "details": "Try at least five unique foods in the last week for balanced nutrition.",
            "progress": f"{min(variety, 5)}/5 foods",
        },
        {
            "id": "streak-sprinter",
            "label": "7-Day Sprinter",
            "achieved": streaks["longest"] >= 7,
            "details": "Maintain a week-long streak of mindful eating logs.",
            "progress": f"{min(streaks['longest'], 7)}/7 days",
        },
    ]
    return achievements


def weekly_summary(meals: List[Dict]) -> Dict:
    weekly_meals = _weekly_window(meals)
    total_calories = sum(meal["calories"] for meal in weekly_meals) if weekly_meals else 0
    avg = total_calories / len(weekly_meals) if weekly_meals else 0
    daily_totals = _daily_totals(weekly_meals)
    best_day = min(daily_totals.items(), key=lambda item: item[1], default=(None, None))
    indulgent_day = max(daily_totals.items(), key=lambda item: item[1], default=(None, None))
    return {
        "totalCalories": round(total_calories, 1),
        "averageCalories": round(avg, 1),
        "count": len(weekly_meals),
        "caloriesByDay": [
            {"date": date.isoformat(), "calories": round(total, 1)}
            for date, total in sorted(daily_totals.items(), key=lambda item: item[0])
        ],
        "bestDay": {"date": best_day[0].isoformat() if best_day[0] else None, "calories": round(best_day[1], 1) if best_day[1] is not None else None},
        "indulgentDay": {
            "date": indulgent_day[0].isoformat() if indulgent_day[0] else None,
            "calories": round(indulgent_day[1], 1) if indulgent_day[1] is not None else None,
        },
    }


def streak_report(meals: List[Dict]) -> Dict[str, int]:
    return {"current": _current_streak(meals), "longest": _longest_streak(meals)}


def coaching_tips(meals: List[Dict], weekly: Optional[Dict] = None) -> List[str]:
    weekly = weekly or weekly_summary(meals)
    tips: List[str] = []
    streaks = streak_report(meals)
    if streaks["current"] < 3:
        tips.append("Log meals three days in a row to unlock the Weekly Habit badge.")
    if weekly["count"] < 5:
        tips.append("Aim for five meals this week to build awareness through repetition.")
    if weekly["averageCalories"] > 750:
        tips.append("Your averages are trending high—try swapping in a lighter lunch or scaling back portions.")
    if weekly["averageCalories"] and weekly["averageCalories"] < 350:
        tips.append("Average calories look low. Make sure you are fueling enough for your activity.")
    if _weekly_variety(meals) < 5:
        tips.append("Add more variety—colorful fruits and veggies can boost micronutrients.")
    if not tips:
        tips.append("Great balance! Keep up the streak and consider setting a macro goal next.")
    return tips[:3]


def _longest_streak(meals: List[Dict]) -> int:
    if not meals:
        return 0
    sorted_meals = sorted(meals, key=lambda meal: _parse_date(meal["created_at"]))
    streak = longest = 1
    for idx in range(1, len(sorted_meals)):
        prev = _parse_date(sorted_meals[idx - 1]["created_at"]).date()
        current = _parse_date(sorted_meals[idx]["created_at"]).date()
        if (current - prev).days <= 1:
            if current == prev:
                continue
            streak += 1
        else:
            streak = 1
        longest = max(longest, streak)
    return longest


def _unique_foods(meals: List[Dict]) -> int:
    names = Counter()
    for meal in meals:
        for food in meal.get("foods", []):
            name = food.get("name")
            if name:
                names[name.lower()] += 1
    return len(names)


def _current_streak(meals: List[Dict]) -> int:
    if not meals:
        return 0
    unique_days = {_parse_date(meal["created_at"]).date() for meal in meals}
    if not unique_days:
        return 0
    today = datetime.utcnow().date()
    streak = 0
    day = today
    if day not in unique_days and (day - timedelta(days=1)) in unique_days:
        day = day - timedelta(days=1)
    while day in unique_days:
        streak += 1
        day -= timedelta(days=1)
    return streak


def _weekly_window(meals: List[Dict]) -> List[Dict]:
    now = datetime.utcnow()
    seven_days_ago = now - timedelta(days=7)
    return [meal for meal in meals if _parse_date(meal["created_at"]) >= seven_days_ago]


def _weekly_variety(meals: List[Dict]) -> int:
    weekly_meals = _weekly_window(meals)
    return _unique_foods(weekly_meals)


def _daily_totals(meals: List[Dict]) -> Dict:
    totals = defaultdict(float)
    for meal in meals:
        day = _parse_date(meal["created_at"]).date()
        totals[day] += float(meal.get("calories", 0))
    return totals
