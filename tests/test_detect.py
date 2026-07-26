from pathlib import Path

from codepulse.detect import detect_project


def test_detect_project_finds_python_files(tmp_path: Path):
    (tmp_path / "main.py").write_text("print('hi')\n")
    (tmp_path / "helper.py").write_text("def f(): pass\n")
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\n")

    profile = detect_project(tmp_path)

    assert profile.languages.get("Python") == 2
    assert "requirements.txt" in profile.manifests
    assert profile.primary_language == "Python"


def test_detect_project_ignores_noise_dirs(tmp_path: Path):
    noisy = tmp_path / "node_modules" / "some_pkg"
    noisy.mkdir(parents=True)
    (noisy / "index.js").write_text("console.log('x')\n")
    (tmp_path / "app.py").write_text("x = 1\n")

    profile = detect_project(tmp_path)

    assert profile.languages.get("JavaScript") is None
    assert profile.languages.get("Python") == 1


def test_detect_project_empty_dir(tmp_path: Path):
    profile = detect_project(tmp_path)
    assert profile.languages == {}
    assert profile.primary_language is None
