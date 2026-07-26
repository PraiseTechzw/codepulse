from pathlib import Path

from codepulse.analyzers import dependencies, docs, smells
from codepulse.analyzers import tests as tests_analyzer
from codepulse.detect import detect_project


def test_docs_analyzer_no_readme(tmp_path: Path):
    result = docs.analyze(tmp_path)
    assert result["details"]["has_readme"] is False
    assert result["score"] == 0


def test_docs_analyzer_good_readme(tmp_path: Path):
    (tmp_path / "README.md").write_text(
        "# My Project\n\n## Installation\n\n## Usage\n\n## License\n\n" + ("word " * 150)
    )
    (tmp_path / "LICENSE").write_text("MIT License")
    result = docs.analyze(tmp_path)
    assert result["details"]["has_readme"] is True
    assert result["details"]["has_license"] is True
    assert result["score"] > 60


def test_dependencies_flags_missing_lockfile(tmp_path: Path):
    (tmp_path / "package.json").write_text("{}")
    result = dependencies.analyze(tmp_path, ["package.json"])
    assert "package.json" in result["details"]["missing_lockfiles"]
    assert result["score"] < 100


def test_dependencies_no_manifests(tmp_path: Path):
    result = dependencies.analyze(tmp_path, [])
    assert result["score"] == 100


def test_smells_detects_todo(tmp_path: Path):
    (tmp_path / "a.py").write_text("# TODO: fix this\nx = 1\n")
    profile = detect_project(tmp_path)
    result = smells.analyze(profile)
    assert result["details"]["todo_fixme_count"] == 1


def test_tests_analyzer_detects_test_files(tmp_path: Path):
    (tmp_path / "app.py").write_text("x = 1\n")
    (tmp_path / "test_app.py").write_text("def test_x(): assert True\n")
    profile = detect_project(tmp_path)
    result = tests_analyzer.analyze(profile)
    assert result["details"]["test_file_count"] == 1
    assert result["details"]["source_file_count"] == 1
