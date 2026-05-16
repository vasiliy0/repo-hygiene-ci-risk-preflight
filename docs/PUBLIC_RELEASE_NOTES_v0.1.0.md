# Release notes draft: v0.1.0

Initial local release candidate for Repository Hygiene / CI Risk Preflight.

## Highlights

- Local no-token repository scan.
- Markdown, JSON, and GitHub annotation output.
- Config file support with ignore rules, path ignores, severity overrides, and baselines.
- CI/repo hygiene rules for deprecated GitHub Actions, local action Node runtime risk, workflow permission risk, release guardrails, CI observability, dependency update config, and core community files.
- Conservative findings with why/fix guidance and stable fingerprints.

## Safety posture

- No GitHub API calls.
- No tokens required.
- No source upload.
- Review findings before failing CI or sharing reports publicly.

## Not included

- No hosted dashboard.
- No GitHub App.
- No marketplace listing.
- No production package registry publish without separate approval.
