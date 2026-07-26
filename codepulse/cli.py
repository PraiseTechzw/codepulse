"""codepulse CLI: scan a project directory and report on its health."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from rich.console import Console

from . import __version__
from .analyzers import dependencies, docs, git_health, smells, structure, tests
from .detect import detect_project
from .git_workflow import build_commit_message, run_git_workflow
from .report import render_markdown_report, render_terminal_report
from .scoring import overall_score


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="codepulse",
        description="Scan a project and report on its health: structure, dependencies, "
        "git activity, docs, tests, and code smells.",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to the project (default: current directory)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output raw JSON instead of a formatted report",
    )
    parser.add_argument("--markdown-out", metavar="FILE", help="Write a Markdown report to FILE")
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip the optional OpenRouter-powered summary",
    )
    parser.add_argument("--version", action="version", version=f"codepulse {__version__}")
    parser.add_argument(
        "--commit-msg",
        metavar="MESSAGE",
        help="Use a custom commit message for the optional Git sync workflow",
    )
    parser.add_argument(
        "--auto-commit",
        action="store_true",
        help="Stage, commit, and push local changes after the scan",
    )
    parser.add_argument(
        "--no-push",
        action="store_true",
        help="Disable pushing when --auto-commit is used",
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        help="Choose an OpenRouter free model (e.g. cohere/north-mini-code:free)",
    )
    return parser


def run_analyzers(root: Path) -> dict:
    profile = detect_project(root)
    return {
        "structure": structure.analyze(profile),
        "git": git_health.analyze(root),
        "dependencies": dependencies.analyze(root, profile.manifests),
        "docs": docs.analyze(root),
        "tests": tests.analyze(profile),
        "smells": smells.analyze(profile),
    }


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    if not root.is_dir():
        print(f"Error: '{root}' is not a directory.", file=sys.stderr)
        return 1

    console = Console()
    with console.status("[bold cyan]Scanning project...[/]"):
        category_results = run_analyzers(root)
        overall = overall_score(category_results)

    llm_summary = None
    if not args.no_llm:
        from .llm import FREE_MODELS, get_llm_summary

        if args.model:
            model_name = args.model
        else:
            model_name = os.environ.get("OPENROUTER_MODEL", "cohere/north-mini-code:free")

        if model_name not in FREE_MODELS and model_name != os.environ.get("OPENROUTER_MODEL"):
            console.print(
                f"[yellow]Model '{model_name}' is not in the built-in free list; attempting anyway.[/]"
            )

        with console.status("[bold cyan]Asking OpenRouter for a summary...[/]"):
            llm_summary = get_llm_summary(
                root.name,
                overall,
                category_results,
                model_name=model_name,
            )

    if args.json:
        import json as json_module

        payload = {
            "project": root.name,
            "overall_score": overall,
            "categories": category_results,
            "llm_summary": llm_summary,
        }
        print(json_module.dumps(payload, indent=2, default=str))
    else:
        render_terminal_report(root.name, overall, category_results, llm_summary, console)

    if args.markdown_out:
        markdown = render_markdown_report(root.name, overall, category_results, llm_summary)
        Path(args.markdown_out).write_text(markdown, encoding="utf-8")
        console.print(f"\n[dim]Markdown report written to {args.markdown_out}[/]")

    if args.auto_commit:
        task_summary = args.commit_msg or build_commit_message(
            root.name, "update project health report"
        )
        success = run_git_workflow(
            root,
            task_summary,
            auto_push=not args.no_push,
        )
        if success:
            console.print("[green]Git workflow completed.[/]")
        else:
            console.print("[yellow]Git workflow skipped or failed.[/]")

    return 0


if __name__ == "__main__":
    sys.exit(main())
