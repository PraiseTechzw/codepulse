"""Scan source files for common code smells and lightweight red flags."""

from __future__ import annotations

import re

from ..detect import ProjectProfile

TODO_PATTERN = re.compile(r"\b(TODO|FIXME|HACK|XXX)\b")
SUSPICIOUS_SECRET_PATTERN = re.compile(
    r"(api[_-]?key|secret|password|token)\s*=\s*['\"][A-Za-z0-9_\-]{8,}['\"]",
    re.IGNORECASE,
)
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".rb",
    ".php",
}


def analyze(profile: ProjectProfile) -> dict:
    todo_count = 0
    suspicious_secrets: list[str] = []

    for path in profile.all_files:
        if path.suffix not in CODE_EXTENSIONS:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

        todo_count += len(TODO_PATTERN.findall(text))

        if SUSPICIOUS_SECRET_PATTERN.search(text):
            suspicious_secrets.append(str(path.relative_to(profile.root)))

    score = 100
    score -= min(30, todo_count * 2)
    score -= min(50, len(suspicious_secrets) * 25)
    score = max(0, score)

    return {
        "score": score,
        "details": {
            "todo_fixme_count": todo_count,
            "possible_hardcoded_secrets": suspicious_secrets[:10],
        },
    }
