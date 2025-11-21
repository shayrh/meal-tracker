import hashlib

from utils.image_recognition import SAMPLED_FOODS, detect_foods


def test_detect_foods_uses_keywords_from_reference():
    reference = "https://example.com/uploads/grilled-chicken-salad.png"

    foods = detect_foods(reference)
    names = [item["name"] for item in foods]

    assert "grilled chicken" in names
    assert "salad" in names
    assert all(food.get("source") == "vision-keyword" for food in foods)


def test_detect_foods_falls_back_to_hash_when_no_keywords():
    reference = "data:image/png;base64,abc123"

    foods = detect_foods(reference)
    expected_idx = int(hashlib.sha256(reference.encode("utf-8")).hexdigest(), 16) % len(SAMPLED_FOODS)

    assert foods
    assert [food["name"] for food in foods] == SAMPLED_FOODS[expected_idx]
    assert all(food.get("source") == "vision-fallback" for food in foods)
