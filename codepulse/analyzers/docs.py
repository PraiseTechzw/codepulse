"""Analyze documentation presence and quality signals."""

from __future__ import annotations

from pathlib import Path

RECOMMENDED_README_SECTIONS = [
    "install",
    "usage",
    "example",
    "license",
    "contribut",
]


def analyze(root: Path) -> dict:
    readme_path = None
    for name in ("README.md", "README.rst", "README.txt", "README"):
        candidate = root / name
        if candidate.exists():
            readme_path = candidate
            break

    has_license = any((root / name).exists() for name in ("LICENSE", "LICENSE.md", "LICENSE.txt"))
    has_contributing = any(
        (root / name).exists() for name in ("CONTRIBUTING.md", "CONTRIBUTING.rst")
    )

    readme_word_count = 0
    sections_found: list[str] = []
    if readme_path:
        text = readme_path.read_text(encoding="utf-8", errors="ignore").lower()
        readme_word_count = len(text.split())
        sections_found = [s for s in RECOMMENDED_README_SECTIONS if s in text]

    score = 0
    if readme_path:
        score += 40
        if readme_word_count > 100:
            score += 15
        score += min(30, len(sections_found) * 8)
    if has_license:
        score += 10
    if has_contributing:
        score += 5
    score = min(100, score)

    return {
        "score": score,
        "details": {
            "has_readme": readme_path is not None,
            "readme_word_count": readme_word_count,
            "readme_sections_found": sections_found,
            "has_license": has_license,
            "has_contributing_guide": has_contributing,
        },
    }
