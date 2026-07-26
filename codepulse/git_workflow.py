"""Helpers for generating commit messages and syncing local changes to GitHub."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from typing import Callable, Sequence


def build_commit_message(
    task_summary: str | None = None, context: str | None = None
) -> str:
    """Build a conventional commit message from task context when available."""

    if context:
        context = context.strip()
        if context:
            return f"chore: {context}"

    if task_summary:
        task_summary = task_summary.strip()
        if task_summary:
            return f"chore: {task_summary}"

    return "chore: update project"


def run_git_workflow(
    repo_path: str | Path,
    message: str | None = None,
    *,
    runner: Callable[[Sequence[str]], subprocess.CompletedProcess[str]] | None = None,
    auto_push: bool = True,
) -> bool:
    """Stage, commit, and optionally push changes in a git repository."""

    repo = Path(repo_path).resolve()
    if not (repo / ".git").exists():
        return False

    if runner is None:
        runner = lambda cmd: subprocess.run(
            cmd, cwd=repo, capture_output=True, text=True, check=False
        )

    commit_message = message or build_commit_message()

    for cmd in (
        ["git", "add", "-A"],
        ["git", "commit", "-m", commit_message],
    ):
        result = runner(cmd)
        if result.returncode != 0:
            return False

    if auto_push:
        pull_result = runner(["git", "pull", "--rebase"])
        if pull_result.returncode != 0:
            return False

        push_result = runner(["git", "push"])
        if push_result.returncode != 0:
            return False

    return True
