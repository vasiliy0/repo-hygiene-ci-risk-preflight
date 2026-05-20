# Repo Hygiene GTM schedule — GitHub Action / Marketplace track

Status: local schedule. External steps require explicit approval.

## Goal

Move `repo-hygiene-ci-risk-preflight` from a CLI/PyPI package to a marketplace-discoverable GitHub Action, then validate whether a GitHub App/SaaS layer is worth building.

## Week 1 — owned surfaces and Action wrapper

1. Local prep: create `action.yml` wrapper around the PyPI package. **Started.**
2. Local prep: write Marketplace approval packet and listing copy. **Started.**
3. Local prep: draft README Action usage section and sample report screenshot/text.
4. Approval gate: push Action wrapper + README/docs to GitHub.
5. Approval gate: create GitHub release/tag `v0.1.0`.

## Week 2 — marketplace-led validation

1. Approval gate: submit/list Action in GitHub Marketplace.
2. Track signals: repo views/clones, stars, issues, PyPI downloads, Marketplace installs/views if available.
3. Prepare one secondary visibility experiment only if needed: Show HN or targeted GitHub Discussion/reply with exact text approval.

## Week 3+ — SaaS/App decision

Build a GitHub App or dashboard only if users ask for org-wide scheduled reports, central policy management, or multi-repo summaries.

## Stop conditions

- No installs/issues/stars after Marketplace listing and README polish: keep as free utility, do not build SaaS.
- Requests are only for rules/CLI usage: improve CLI/Action, not dashboard.
- Requests include org-wide scheduled reporting: prepare GitHub App approval packet with minimal read-only scopes.
