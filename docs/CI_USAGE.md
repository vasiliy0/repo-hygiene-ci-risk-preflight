# CI usage

Repository Hygiene / CI Risk Preflight is designed for checked-out repositories and requires no GitHub token.

## GitHub Actions summary report

```yaml
name: repo-hygiene-preflight

on:
  pull_request:
  workflow_dispatch:

permissions:
  contents: read

jobs:
  hygiene:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Install scanner
        run: python -m pip install repo-hygiene-ci-risk-preflight
      - name: Write Markdown report
        run: |
          repo-hygiene-preflight . --format markdown --output repo-hygiene-report.md
          cat repo-hygiene-report.md >> "$GITHUB_STEP_SUMMARY"
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: repo-hygiene-report
          path: repo-hygiene-report.md
```

## CI gate

Start with a non-blocking report. After the team reviews false positives, gate on high severity only:

```bash
repo-hygiene-preflight . --fail-on-severity high
```

## GitHub annotations

```bash
repo-hygiene-preflight . --format annotations
```

The annotation output uses workflow commands and is intended for GitHub Actions logs. Review rules before making it blocking.

## Baseline existing findings

For repos with known existing issues:

```bash
repo-hygiene-preflight . --format json --output report.json --write-baseline repo-hygiene-baseline.json
repo-hygiene-preflight . --baseline repo-hygiene-baseline.json --fail-on-severity high
```

Commit the baseline only if your team accepts it. Remove fingerprints as findings are fixed.
