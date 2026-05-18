# Repository Hygiene / CI Risk Preflight

Local no-token scanner for GitHub repository hygiene, CI policy, and release-readiness signals before they become public repo or package release blockers.

Use this before opening a public repo, adding CI gates, publishing a package, or preparing a release checklist. It is broader than the GitHub Actions deprecation scanner: this tool checks repo/package/release hygiene, not only action-version migration risks.

This is the bridge product in the Engineering Risk Preflight suite: it starts as a CLI, can be used in GitHub Actions, and can later inform a GitHub App/SaaS only after demand is validated.

## What it checks

The scanner reads only files in a checked-out repository. It does **not** use the GitHub API, tokens, network calls, SaaS accounts, private repo integrations, or source uploads.

Current rule categories:

- `ci-deprecation`: stale GitHub Actions majors such as `upload-artifact@v3`, `download-artifact@v3`, `cache@v3`, `checkout@v3`, `setup-node@v3`.
- `ci-runtime`: local JavaScript actions using old Node runtimes.
- `ci-permissions`: broad workflow permissions such as `write-all`, `contents: write`, and `pull_request_target` review prompts.
- `repo-hygiene`: missing `CODEOWNERS`, `SECURITY.md`, `CONTRIBUTING.md`, and changelog/release history.
- `dependency-hygiene`: missing Dependabot/Renovate config.
- `ci-observability`: missing test report artifacts/summaries and artifact upload steps without `if: always()`.
- `release-safety`: release/publish workflows without visible guardrails.
- `ci-cost`: jobs without visible `timeout-minutes`.

## Repository readiness story

Top checks to run before a repo or package is promoted publicly:

1. Is there a visible license/security/contribution posture?
2. Are CI workflows using risky broad permissions or `pull_request_target` patterns?
3. Are release/publish jobs guarded by tags, manual dispatch, environments, or explicit conditions?
4. Are test reports and failure artifacts preserved for debugging?
5. Are dependency update tools configured?
6. Are stale action majors or local Node runtimes likely to break CI later?

Sample report excerpt:

```text
- high `workflow-write-all-permissions`
  - Why: Broad workflow permissions increase blast radius if a workflow is abused.
  - Fix: Prefer least-privilege `permissions:` at workflow/job scope.

- medium `missing-security-policy`
  - Why: Public repos should tell users how to report vulnerabilities.
  - Fix: Add SECURITY.md with supported versions and a private reporting path.
```

## Install from PyPI

```bash
python3 -m pip install repo-hygiene-ci-risk-preflight
repo-hygiene-preflight path/to/repo --format markdown
repo-hygiene-preflight path/to/repo --format json
repo-hygiene-preflight path/to/repo --format annotations
repo-hygiene-preflight path/to/repo --fail-on-severity high
repo-hygiene-preflight --list-rules
```

PyPI: https://pypi.org/project/repo-hygiene-ci-risk-preflight/

## Try from a clone

```bash
python3 scanner.py examples
python3 scanner.py examples --format json
python3 scanner.py examples --format annotations
python3 scanner.py examples --min-severity medium
python3 scanner.py examples --fail-on-severity high
python3 scanner.py --list-rules
```

Generated example reports:

- [`examples/report.md`](examples/report.md)
- [`examples/report.json`](examples/report.json)
- [`examples/annotations.txt`](examples/annotations.txt)

## GitHub Action wrapper (planned)

A Marketplace-friendly GitHub Action wrapper is being prepared. The intended usage is:

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
      - uses: vasiliy0/repo-hygiene-ci-risk-preflight@v0.1.0
        with:
          format: markdown
          output: repo-hygiene-report.md
```

Until the Action is released, use the PyPI install flow above in CI.

## Config and baselines

Auto-load `.repo-hygiene-preflight.json` or pass `--config`:

```json
{
  "ignore_rules": ["workflow-without-timeout"],
  "only_rules": [],
  "ignore_paths": ["docs/generated/**"],
  "severity_overrides": {"missing-contributing": "info"},
  "baseline_fingerprints": []
}
```

Baseline existing findings for gradual rollout:

```bash
python3 scanner.py . --format json --output report.json --write-baseline repo-hygiene-baseline.json
python3 scanner.py . --baseline repo-hygiene-baseline.json --fail-on-severity high
```

## Outputs

- Markdown report for local review or `$GITHUB_STEP_SUMMARY`.
- JSON report for CI artifacts or later policy processing.
- GitHub workflow annotation commands via `--format annotations`.
- Stable finding fingerprints for suppressions and baselines.

## Docs

- `docs/RULE_INVENTORY.md` — current rule inventory.
- `docs/CONFIGURATION.md` — config and baseline behavior.
- `docs/CI_USAGE.md` — GitHub Actions usage patterns.
- `docs/GITHUB_ACTION_DRAFT.md` — local design artifact for a future wrapper action.
- `docs/PYPI_TESTPYPI_READINESS.md` — package readiness checklist.

## Privacy posture

- Local files only.
- No GitHub token required.
- No source upload.
- Findings include file paths and matching lines; review before sharing publicly.
- Rules are conservative preflight signals, not compliance/security guarantees.

## Related Engineering Risk Preflight tools

- [GitHub Actions Deprecation Preflight](https://github.com/vasiliy0/github-actions-deprecation-preflight) — focused action-major/runtime migration checks for workflows.
- [Zod OpenAPI Contract Lint Kit](https://github.com/vasiliy0/zod-openapi-contract-lint-kit) — API contract drift checks for Zod/OpenAPI projects.
- [Playwright Flake Triage Toolkit](https://github.com/vasiliy0/playwright-flake-triage) — local triage for flaky Playwright reports and CI logs.

## Monetization hypothesis

Free CLI/GitHub Action first. Paid add-ons later only after demand validation: team policy packs, release-readiness rule bundles, scheduled org reports, or an org dashboard.
