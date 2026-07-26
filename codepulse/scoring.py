"""Combine per-category scores into an overall project health score."""

from __future__ import annotations

# category -> weight (must sum to 1.0)
CATEGORY_WEIGHTS: dict[str, float] = {
    "structure": 0.15,
    "git": 0.15,
    "dependencies": 0.20,
    "docs": 0.15,
    "tests": 0.25,
    "smells": 0.10,
}


def overall_score(category_results: dict[str, dict]) -> int:
    total = 0.0
    weight_sum = 0.0
    for category, weight in CATEGORY_WEIGHTS.items():
        result = category_results.get(category)
        if result is None:
            continue
        total += result["score"] * weight
        weight_sum += weight
    if weight_sum == 0:
        return 0
    return round(total / weight_sum)


def grade_for_score(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "F"
