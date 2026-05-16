# Repo Hygiene CI Risk Preflight rules

## `upload-artifact-v3`
- Severity: `high`
- Category: `ci-deprecation`
- Confidence: `high`
- Why: upload-artifact v3 is retired for new runs and can break CI/report publishing.
- Fix: Upgrade to actions/upload-artifact@v4 and verify retention/name/path behavior.
- Pattern: `uses\s*:\s*actions/upload-artifact@v3\b`

## `download-artifact-v3`
- Severity: `high`
- Category: `ci-deprecation`
- Confidence: `high`
- Why: download-artifact v3 is retired alongside upload-artifact v3.
- Fix: Upgrade to actions/download-artifact@v4 and test artifact names/merge behavior.
- Pattern: `uses\s*:\s*actions/download-artifact@v3\b`

## `cache-v3-review`
- Severity: `medium`
- Category: `ci-deprecation`
- Confidence: `medium`
- Why: Older cache action majors should be reviewed before runtime/service changes bite CI.
- Fix: Plan upgrade to actions/cache@v4 and verify key/restore-key behavior.
- Pattern: `uses\s*:\s*actions/cache@v3\b`

## `checkout-v3-review`
- Severity: `medium`
- Category: `ci-deprecation`
- Confidence: `medium`
- Why: Older checkout major versions can lag runtime/security maintenance.
- Fix: Upgrade to actions/checkout@v4 and verify submodule/LFS/token behavior if used.
- Pattern: `uses\s*:\s*actions/checkout@v3\b`

## `setup-node-v3-review`
- Severity: `medium`
- Category: `ci-deprecation`
- Confidence: `medium`
- Why: Older setup-node major versions should be reviewed before runtime/cache behavior changes.
- Fix: Upgrade to actions/setup-node@v4 and verify cache/node-version behavior.
- Pattern: `uses\s*:\s*actions/setup-node@v3\b`

## `local-action-node16`
- Severity: `high`
- Category: `ci-runtime`
- Confidence: `high`
- Why: Local JavaScript action metadata uses an obsolete Node runtime.
- Fix: Move the local action to a supported Node runtime and test it in CI.
- Pattern: `(?:runs\.using|using)\s*:\s*[\"']?node16[\"']?`

## `workflow-write-all-permissions`
- Severity: `high`
- Category: `ci-permissions`
- Confidence: `medium`
- Why: Workflow uses broad write-all permissions, increasing blast radius if a token is exposed or a job is compromised.
- Fix: Replace write-all with least-privilege job/workflow permissions.
- Pattern: `permissions\s*:\s*write-all\b`

## `workflow-contents-write`
- Severity: `medium`
- Category: `ci-permissions`
- Confidence: `medium`
- Why: contents: write can mutate repository contents and should be limited to jobs that need it.
- Fix: Scope contents: write to release/publish jobs and prefer contents: read elsewhere.
- Pattern: `contents\s*:\s*write\b`

## `pull-request-target-review`
- Severity: `high`
- Category: `ci-permissions`
- Confidence: `medium`
- Why: pull_request_target runs with elevated context and is risky with untrusted fork code.
- Fix: Use pull_request when possible; if pull_request_target is needed, avoid checking out untrusted code and minimize permissions.
- Pattern: `pull_request_target\s*:`

## `missing-codeowners`
- Severity: `medium`
- Category: `repo-hygiene`
- Confidence: `high`
- Why: No CODEOWNERS file was found.
- Fix: Add CODEOWNERS under root, .github/, or docs/ to make review ownership explicit.

## `missing-security-policy`
- Severity: `medium`
- Category: `repo-hygiene`
- Confidence: `high`
- Why: No SECURITY.md policy was found.
- Fix: Add SECURITY.md with supported versions and vulnerability reporting instructions.

## `missing-contributing`
- Severity: `low`
- Category: `repo-hygiene`
- Confidence: `high`
- Why: No CONTRIBUTING.md guide was found.
- Fix: Add a short contribution and local test guide.

## `missing-changelog`
- Severity: `low`
- Category: `repo-hygiene`
- Confidence: `high`
- Why: No changelog/release history file was found.
- Fix: Add CHANGELOG.md or document where release notes live.

## `missing-dependabot-config`
- Severity: `low`
- Category: `dependency-hygiene`
- Confidence: `medium`
- Why: No Dependabot/Renovate config was found.
- Fix: Add Dependabot or Renovate config if dependency update automation is appropriate for this repo.

## `missing-ci-report-artifact`
- Severity: `medium`
- Category: `ci-observability`
- Confidence: `medium`
- Why: Test-heavy CI is harder to debug when reports disappear after failed runs.
- Fix: Upload test reports/logs with actions/upload-artifact@v4 or write a concise $GITHUB_STEP_SUMMARY.

## `artifact-upload-without-always`
- Severity: `low`
- Category: `ci-observability`
- Confidence: `medium`
- Why: Report upload steps can be skipped when earlier test steps fail.
- Fix: Use `if: always()` on report/artifact upload steps where safe.

## `release-workflow-without-guardrail`
- Severity: `high`
- Category: `release-safety`
- Confidence: `medium`
- Why: Release/publish workflows are reputation-impacting and should have an explicit guardrail.
- Fix: Add workflow_dispatch, protected environment approvals, or a documented confirmation gate.

## `workflow-without-timeout`
- Severity: `low`
- Category: `ci-cost`
- Confidence: `low`
- Why: Jobs without timeouts can hang and waste runner minutes.
- Fix: Add `timeout-minutes` to long-running or externally-dependent jobs.
