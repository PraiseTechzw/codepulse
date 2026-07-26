"""Analyze git repository health: activity, contributors, working tree state."""

from __future__ import annotations

import subprocess
from datetime import datetime, timezone
from pathlib import Path


def _run_git(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return None
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def analyze(root: Path) -> dict:
    if not (root / ".git").exists():
        return {
            "score": 50,
            "details": {"is_git_repo": False},
        }

    last_commit_raw = _run_git(root, "log", "-1", "--format=%ct")
    contributors_raw = _run_git(root, "shortlog", "-sn", "--all")
    status_raw = _run_git(root, "status", "--porcelain")
    commit_count_raw = _run_git(root, "rev-list", "--count", "HEAD")

    days_since_commit = None
    if last_commit_raw:
        last_commit_dt = datetime.fromtimestamp(int(last_commit_raw), tz=timezone.utc)
        days_since_commit = (datetime.now(timezone.utc) - last_commit_dt).days

    contributor_count = len(contributors_raw.splitlines()) if contributors_raw else 0
    uncommitted_changes = len(status_raw.splitlines()) if status_raw else 0
    commit_count = int(commit_count_raw) if commit_count_raw and commit_count_raw.isdigit() else 0

    score = 100
    if days_since_commit is not None:
        if days_since_commit > 365:
            score -= 40
        elif days_since_commit > 90:
            score -= 20
        elif days_since_commit > 30:
            score -= 10
    if uncommitted_changes > 20:
        score -= 15
    elif uncommitted_changes > 0:
        score -= 5
    score = max(0, score)

    return {
        "score": score,
        "details": {
            "is_git_repo": True,
            "days_since_last_commit": days_since_commit,
            "contributor_count": contributor_count,
            "uncommitted_changes": uncommitted_changes,
            "total_commits": commit_count,
        },
    }
