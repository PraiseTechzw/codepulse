# codepulse

![CI](https://github.com/yourname/codepulse/actions/workflows/ci.yml/badge.svg)

A CLI that takes the pulse of a codebase. Point it at any project — Python,
JavaScript, Go, Rust, whatever — and it scans structure, dependencies, git
activity, documentation, tests, and code smells, then hands you a single
health score plus a category breakdown. Add an `OPENROUTER_API_KEY` and it'll
also ask OpenRouter for a short, prioritized "here's what to fix first" summary.

## Installation

```bash
git clone https://github.com/yourname/codepulse.git
cd codepulse
pip install -e .

# optional: enable the OpenRouter-powered summary
pip install -e ".[llm]"
```

## Usage

```bash
# Scan the current directory
codepulse

# Scan a specific project
codepulse /path/to/project

# Skip the LLM summary (pure static analysis, no API key needed)
codepulse . --no-llm

# Machine-readable output
codepulse . --json

# Write a shareable Markdown report
codepulse . --markdown-out health-report.md

# Auto-commit and push any local changes after the scan
codepulse . --auto-commit --commit-msg "chore: update analysis"
```

To enable the OpenRouter-powered summary, set your API key first:

```bash
export OPENROUTER_API_KEY=your-openrouter-key
codepulse .
```

## Example output

```
╭──────────────────────────────────────────────────────────────╮
│ my-project — Health Score: 78/100 (C)                        │
╰──────────────────────────────────────────────────────────────╯
┏━━━━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Category      ┃ Score ┃ Key Findings                       ┃
┡━━━━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Structure     │   100 │ 42 files, 5,120 lines...            │
│ Git Activity  │    90 │ 314 commits, 3 contributors...      │
│ Dependencies  │    70 │ Missing lockfiles: package.json...  │
│ Documentation │    85 │ README: yes (410 words)...          │
│ Test Coverage │    55 │ 8 test file(s) vs 34 source...      │
│ Code Smells   │    95 │ 3 TODO/FIXME marker(s)...           │
└───────────────┴───────┴─────────────────────────────────────┘
```

## What it checks

| Category          | Signals                                                            |
| ----------------- | ------------------------------------------------------------------ |
| **Structure**     | Language mix, total files/lines, oversized files (>500 lines)      |
| **Git Activity**  | Commit recency, contributor count, uncommitted changes             |
| **Dependencies**  | Manifest/lockfile pairing, unpinned versions in `requirements.txt` |
| **Documentation** | README presence/length/sections, LICENSE, CONTRIBUTING guide       |
| **Test Coverage** | Ratio of test files to source files                                |
| **Code Smells**   | TODO/FIXME/HACK density, patterns resembling hardcoded secrets     |

Each category is scored 0–100 and combined into a weighted overall score
(tests and dependencies are weighted heaviest, since they tend to matter most
for long-term project health).

## Design notes

- **Everything works with zero configuration and no API key.** The LLM step
  is a pure bonus layer — if `OPENROUTER_API_KEY` isn't set, `codepulse` just
  skips it silently.
- **Multi-language by design.** Detection is extension- and manifest-based
  rather than hardcoded to one ecosystem, so it adapts to whatever language(s)
  it finds in the project.
- **No code is ever sent anywhere.** Only aggregated metrics (counts, ratios,
  filenames) are sent to Claude for the optional summary — never file
  contents.

## Extending it

Each analyzer lives in `codepulse/analyzers/` as a standalone module with a
single `analyze(...)` function that returns `{"score": int, "details": dict}`.
To add a new category:

1. Create `codepulse/analyzers/your_check.py` with an `analyze()` function.
2. Wire it into `run_analyzers()` in `codepulse/cli.py`.
3. Add a weight for it in `CATEGORY_WEIGHTS` in `codepulse/scoring.py`.
4. Add a label/summary line in `codepulse/report.py`.

## Running the test suite

```bash
pip install -e ".[dev]"
pytest tests/
```

## Continuous Integration

Every push and pull request to `main` runs through [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. **Lint** — `ruff check` and `ruff format --check`
2. **Test** — `pytest` on Python 3.9 through 3.12
3. **Smoke test** — installs the package and runs `codepulse` against its own repo

Run the same checks locally before pushing:

```bash
pip install -e ".[dev]"
ruff check .
ruff format --check .
pytest tests/ -v
```

## License

MIT — see [LICENSE](LICENSE).
