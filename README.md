# Repository Hygiene / CI Risk Preflight

Local no-token scanner for GitHub repository hygiene and CI risk signals before they become release blockers.

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

## Try locally

```bash
python3 scanner.py examples
python3 scanner.py examples --format json
python3 scanner.py examples --format annotations
python3 scanner.py examples --min-severity medium
python3 scanner.py examples --fail-on-severity high
python3 scanner.py --list-rules
```

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

## Monetization hypothesis

Free CLI/GitHub Action first. Paid add-ons later only after demand validation: team policy packs, release-readiness rule bundles, scheduled org reports, or an org dashboard.
