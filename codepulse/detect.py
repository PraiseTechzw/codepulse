"""Detect which languages, frameworks, and manifest files a project uses."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

# Maps file extension -> language display name
EXTENSION_LANGUAGE_MAP: dict[str, str] = {
    ".py": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".m": "Objective-C",
    ".scala": "Scala",
    ".ex": "Elixir",
    ".exs": "Elixir",
}

# Manifest file name -> (ecosystem name, dependency file kind)
MANIFEST_FILES: dict[str, str] = {
    "requirements.txt": "pip",
    "pyproject.toml": "pip/poetry",
    "Pipfile": "pipenv",
    "package.json": "npm",
    "yarn.lock": "yarn",
    "pnpm-lock.yaml": "pnpm",
    "Cargo.toml": "cargo",
    "go.mod": "go modules",
    "pom.xml": "maven",
    "build.gradle": "gradle",
    "build.gradle.kts": "gradle",
    "Gemfile": "bundler",
    "composer.json": "composer",
}

IGNORED_DIRS = {
    ".git",
    "node_modules",
    "venv",
    ".venv",
    "__pycache__",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    "target",
    ".idea",
    ".vscode",
    "vendor",
    "coverage",
    ".next",
    ".nuxt",
    "egg-info",
}


@dataclass
class ProjectProfile:
    root: Path
    languages: dict[str, int] = field(default_factory=dict)  # language -> file count
    manifests: list[str] = field(default_factory=list)
    all_files: list[Path] = field(default_factory=list)

    @property
    def primary_language(self) -> str | None:
        if not self.languages:
            return None
        return max(self.languages, key=self.languages.get)


def iter_project_files(root: Path):
    """Yield all files under root, skipping common noise directories."""
    for path in root.rglob("*"):
        if any(part in IGNORED_DIRS for part in path.parts):
            continue
        if path.is_file():
            yield path


def detect_project(root: Path) -> ProjectProfile:
    profile = ProjectProfile(root=root)
    for path in iter_project_files(root):
        profile.all_files.append(path)
        lang = EXTENSION_LANGUAGE_MAP.get(path.suffix)
        if lang:
            profile.languages[lang] = profile.languages.get(lang, 0) + 1
        if path.name in MANIFEST_FILES and path.parent == root:
            profile.manifests.append(path.name)
    return profile
