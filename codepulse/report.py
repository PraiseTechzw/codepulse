"""Render the health report to the terminal (rich) and to Markdown."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from .scoring import grade_for_score

CATEGORY_LABELS = {
    "structure": "Structure",
    "git": "Git Activity",
    "dependencies": "Dependencies",
    "docs": "Documentation",
    "tests": "Test Coverage",
    "smells": "Code Smells",
}


def _score_color(score: int) -> str:
    if score >= 80:
        return "green"
    if score >= 60:
        return "yellow"
    return "red"


def render_terminal_report(
    project_name: str,
    overall: int,
    category_results: dict[str, dict],
    llm_summary: str | None,
    console: Console | None = None,
) -> None:
    console = console or Console()
    grade = grade_for_score(overall)

    header = Text(
        f"{project_name} — Health Score: {overall}/100 ({grade})", style="bold"
    )
    console.print(Panel(header, style=_score_color(overall)))

    table = Table(show_header=True, header_style="bold")
    table.add_column("Category")
    table.add_column("Score", justify="right")
    table.add_column("Key Findings")

    for key, label in CATEGORY_LABELS.items():
        result = category_results.get(key)
        if not result:
            continue
        score = result["score"]
        findings = _summarize_details(key, result["details"])
        table.add_row(label, f"[{_score_color(score)}]{score}[/]", findings)

    console.print(table)

    if llm_summary:
        console.print(Panel(llm_summary, title="OpenRouter's Take", style="cyan"))


def _summarize_details(category: str, details: dict) -> str:
    if category == "structure":
        langs = ", ".join(
            f"{k} ({v})" for k, v in list(details.get("languages", {}).items())[:3]
        )
        large = len(details.get("large_files", []))
        return (
            f"{details.get('total_code_files', 0)} files, {details.get('total_lines', 0)} lines. "
            f"Languages: {langs or 'none detected'}. {large} oversized file(s)."
        )
    if category == "git":
        if not details.get("is_git_repo"):
            return "Not a git repository."
        days = details.get("days_since_last_commit")
        return (
            f"{details.get('total_commits', 0)} commits, {details.get('contributor_count', 0)} contributor(s), "
            f"last commit {days} day(s) ago, {details.get('uncommitted_changes', 0)} uncommitted change(s)."
        )
    if category == "dependencies":
        missing = details.get("missing_lockfiles", [])
        unpinned = details.get("unpinned_dependencies", 0)
        return (
            f"Manifests: {', '.join(details.get('manifests_found', [])) or 'none'}. "
            f"Missing lockfiles: {', '.join(missing) or 'none'}. Unpinned deps: {unpinned}."
        )
    if category == "docs":
        return (
            f"README: {'yes' if details.get('has_readme') else 'no'} "
            f"({details.get('readme_word_count', 0)} words). "
            f"LICENSE: {'yes' if details.get('has_license') else 'no'}."
        )
    if category == "tests":
        return (
            f"{details.get('test_file_count', 0)} test file(s) vs "
            f"{details.get('source_file_count', 0)} source file(s) "
            f"(ratio {details.get('test_to_source_ratio', 0)})."
        )
    if category == "smells":
        secrets = details.get("possible_hardcoded_secrets", [])
        note = f" ⚠ {len(secrets)} possible hardcoded secret(s)!" if secrets else ""
        return f"{details.get('todo_fixme_count', 0)} TODO/FIXME marker(s).{note}"
    return ""


def render_markdown_report(
    project_name: str,
    overall: int,
    category_results: dict[str, dict],
    llm_summary: str | None,
) -> str:
    grade = grade_for_score(overall)
    lines = [
        f"# {project_name} — Health Report",
        "",
        f"**Overall score:** {overall}/100 ({grade})",
        "",
    ]
    lines.append("| Category | Score | Key Findings |")
    lines.append("|---|---|---|")
    for key, label in CATEGORY_LABELS.items():
        result = category_results.get(key)
        if not result:
            continue
        findings = _summarize_details(key, result["details"])
        lines.append(f"| {label} | {result['score']} | {findings} |")

    if llm_summary:
        lines += ["", "## OpenRouter's Take", "", llm_summary]

    return "\n".join(lines) + "\n"
