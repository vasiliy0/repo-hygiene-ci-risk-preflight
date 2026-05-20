# GitHub Action / Marketplace approval packet — Repository Hygiene / CI Risk Preflight

Status: local preparation only. Do not push `action.yml`, create a release/tag, submit a Marketplace listing, or change repo metadata without explicit approval.

## Proposed marketplace form

A GitHub Action wrapper around the published PyPI package `repo-hygiene-ci-risk-preflight==0.1.1`.

## Listing positioning

- Name: Repository Hygiene / CI Risk Preflight
- One-liner: No-token repository hygiene and CI risk scan for stale Actions, release guardrails, ownership docs, and CI observability gaps.
- Category fit: CI, code quality, project management / utilities.
- Privacy: local checkout only; no GitHub token required; no network calls except installing the public package from PyPI.

## Marketplace/search keywords

`github-actions`, `ci`, `repository-hygiene`, `release-readiness`, `codeowners`, `security-md`, `deprecated-actions`, `ci-observability`, `devops`, `platform-engineering`.

## Minimal workflow example

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
      - uses: vasiliy0/repo-hygiene-ci-risk-preflight@v0.1.1
        with:
          format: markdown
          output: repo-hygiene-report.md
      - if: always()
        uses: actions/upload-artifact@v4
        with:
          name: repo-hygiene-report
          path: repo-hygiene-report.md
```

## Release/listing prerequisites

- [ ] Review `action.yml` locally.
- [ ] Update README with Action usage section and Marketplace-oriented screenshots/sample report.
- [ ] Push `action.yml` and docs to GitHub after approval.
- [ ] Create GitHub release/tag `v0.1.1` after approval.
- [ ] Confirm GitHub Marketplace listing requirements from the repo UI.
- [ ] Submit/list the Action after approval.

## Explicitly not included

No GitHub App registration, OAuth permissions, private repo access, payment/Sponsors setup, ads, DEV.to post, DMs, Reddit/HN posts, or broad campaign.

## Approval ask to use later

Approve pushing the GitHub Action wrapper and Marketplace-ready README/docs for `vasiliy0/repo-hygiene-ci-risk-preflight`; no release/tag, Marketplace submission, outreach, GitHub App, or payment setup.
