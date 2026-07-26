"""Analyze project structure: size, language mix, oversized files."""

from __future__ import annotations

from pathlib import Path

from ..detect import ProjectProfile

LARGE_FILE_LINE_THRESHOLD = 500
CODE_EXTENSIONS = {
    ".py",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".go",
    ".rs",
    ".java",
    ".kt",
    ".rb",
    ".php",
    ".c",
    ".h",
    ".cpp",
    ".hpp",
    ".cs",
    ".swift",
    ".m",
    ".scala",
    ".ex",
    ".exs",
}


def _count_lines(path: Path) -> int:
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            return sum(1 for _ in f)
    except OSError:
        return 0


def analyze(profile: ProjectProfile) -> dict:
    code_files = [p for p in profile.all_files if p.suffix in CODE_EXTENSIONS]
    total_lines = 0
    large_files: list[tuple[str, int]] = []

    for path in code_files:
        lines = _count_lines(path)
        total_lines += lines
        if lines > LARGE_FILE_LINE_THRESHOLD:
            large_files.append((str(path.relative_to(profile.root)), lines))

    large_files.sort(key=lambda x: -x[1])

    score = 100
    if code_files:
        oversized_ratio = len(large_files) / len(code_files)
        score -= min(60, int(oversized_ratio * 200))
    score = max(0, score)

    return {
        "score": score,
        "details": {
            "total_code_files": len(code_files),
            "total_lines": total_lines,
            "languages": profile.languages,
            "large_files": large_files[:10],
        },
    }
