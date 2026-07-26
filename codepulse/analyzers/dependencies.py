"""Analyze dependency management health across ecosystems."""

from __future__ import annotations

import re
from pathlib import Path

# manifest filename -> expected lockfile filename(s)
LOCKFILE_EXPECTATIONS: dict[str, list[str]] = {
    "package.json": ["package-lock.json", "yarn.lock", "pnpm-lock.yaml"],
    "pyproject.toml": ["poetry.lock", "uv.lock"],
    "Pipfile": ["Pipfile.lock"],
    "Cargo.toml": ["Cargo.lock"],
    "Gemfile": ["Gemfile.lock"],
    "composer.json": ["composer.lock"],
}

UNPINNED_PATTERN = re.compile(r"^[A-Za-z0-9_.\-]+\s*$")  # a bare name, no version spec


def _check_requirements_txt(path: Path) -> tuple[int, int]:
    """Return (total_deps, unpinned_deps) for a requirements.txt file."""
    total = 0
    unpinned = 0
    try:
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("-"):
                continue
            total += 1
            if not any(op in line for op in ("==", ">=", "<=", "~=", ">", "<")):
                unpinned += 1
    except OSError:
        pass
    return total, unpinned


def analyze(root: Path, manifests: list[str]) -> dict:
    if not manifests:
        return {
            "score": 100,
            "details": {"manifests_found": [], "note": "No dependency manifests detected."},
        }

    missing_lockfiles = []
    for manifest in manifests:
        expected = LOCKFILE_EXPECTATIONS.get(manifest)
        if not expected:
            continue
        if not any((root / lock).exists() for lock in expected):
            missing_lockfiles.append(manifest)

    unpinned_total = 0
    deps_total = 0
    req_file = root / "requirements.txt"
    if req_file.exists():
        deps_total, unpinned_total = _check_requirements_txt(req_file)

    score = 100
    score -= min(50, 25 * len(missing_lockfiles))
    if deps_total:
        score -= min(30, int((unpinned_total / deps_total) * 30))
    score = max(0, score)

    return {
        "score": score,
        "details": {
            "manifests_found": manifests,
            "missing_lockfiles": missing_lockfiles,
            "unpinned_dependencies": unpinned_total,
            "total_dependencies_checked": deps_total,
        },
    }
