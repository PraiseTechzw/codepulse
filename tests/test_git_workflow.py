import subprocess
from pathlib import Path

from codepulse.git_workflow import build_commit_message, run_git_workflow


def test_build_commit_message_prefers_context(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    message = build_commit_message("openrouter integration", "update docs")
    assert message == "chore: update docs"


def test_run_git_workflow_commits_and_pushes(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "README.md").write_text("hello", encoding="utf-8")
    subprocess.run(["git", "init"], check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test User"], check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], check=True)

    class FakeRunner:
        def __init__(self):
            self.calls = []

        def __call__(self, cmd):
            self.calls.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    runner = FakeRunner()
    result = run_git_workflow(tmp_path, "update docs", runner=runner)

    assert result is True
    assert runner.calls[0][:2] == ["git", "add"]
    assert any(call[:2] == ["git", "commit"] for call in runner.calls)
    assert any(call[:2] == ["git", "push"] for call in runner.calls)
