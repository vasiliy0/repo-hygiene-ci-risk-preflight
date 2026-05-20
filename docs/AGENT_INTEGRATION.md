# AI agent and CI integration

This CLI is safe for agent workflows that need a no-token repository hygiene, CI risk, and release-readiness preflight.

## When an agent should run it

Run `repo-hygiene-preflight` before public repo publication, package release, CI gate changes, or release-readiness reviews. Use findings as review prompts, not as compliance guarantees.

## Safe commands

```bash
repo-hygiene-preflight . --format json --output repo-hygiene-report.json --quiet --no-color
repo-hygiene-preflight . --format annotations
repo-hygiene-preflight . --fail-on-severity high
repo-hygiene-preflight . --format json --write-baseline repo-hygiene-baseline.json
```

## Machine contract

- JSON schema: `schemas/report.schema.json`.
- `schema_version`: `1.0`.
- Findings include `rule_id`, `severity`, `category`, `file`, `line`, `signal`, `why`, `fix`, `confidence`, and `fingerprint`.
- Baselines suppress accepted existing fingerprints for gradual rollout.

## Exit codes

- `0`: scan completed; report-only mode or no configured gate was tripped.
- `1`: scan completed and `--fail-on-severity` matched.
- `2`: usage/config/input error from the CLI parser.
- `3`: reserved for future runtime/tool errors.

## Agent loop

1. Run JSON mode on a checked-out repo.
2. Parse high/medium findings and fingerprints.
3. Prepare a PR checklist: workflow permissions, release guardrails, missing docs, CI observability, dependency automation.
4. Ask before editing files or pushing.
5. Rerun and confirm fixed fingerprints disappear; do not hide new findings without explanation.

## Safety

The tool reads local repo files only. It uses no GitHub API, token, network calls, telemetry, or source upload. Reports include file paths and matched lines; review before sharing.
