"""Analyze presence of a test suite relative to source code volume."""

from __future__ import annotations

from ..detect import ProjectProfile

TEST_MARKERS = ("test_", "_test", ".test.", ".spec.", "tests/", "test/", "spec/", "__tests__/")


def _looks_like_test(path_str: str) -> bool:
    lowered = path_str.lower()
    return any(marker in lowered for marker in TEST_MARKERS)


def analyze(profile: ProjectProfile) -> dict:
    code_files = [
        p
        for p in profile.all_files
        if p.suffix in {".py", ".js", ".jsx", ".ts", ".tsx", ".go", ".rs", ".java", ".rb"}
    ]
    test_files = [p for p in code_files if _looks_like_test(str(p.relative_to(profile.root)))]
    non_test_files = [p for p in code_files if p not in test_files]

    ratio = len(test_files) / len(non_test_files) if non_test_files else 0

    if not code_files:
        score = 100
    elif not test_files:
        score = 10
    else:
        score = min(100, 40 + int(ratio * 200))

    return {
        "score": score,
        "details": {
            "test_file_count": len(test_files),
            "source_file_count": len(non_test_files),
            "test_to_source_ratio": round(ratio, 2),
        },
    }
