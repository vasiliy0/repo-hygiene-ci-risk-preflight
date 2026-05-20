# Repository Hygiene / CI Risk Preflight

Scanned workflows: 2
Scanned files: 5
Active rules: 18
Findings: 13

## Summary by severity
- **high**: 3
- **low**: 6
- **medium**: 4

## Summary by category
- `ci-cost`: 2
- `ci-deprecation`: 2
- `ci-observability`: 2
- `ci-runtime`: 1
- `dependency-hygiene`: 1
- `release-safety`: 1
- `repo-hygiene`: 4

## Summary by rule
- `artifact-upload-without-always`: 1
- `checkout-v3-review`: 1
- `local-action-node16`: 1
- `missing-changelog`: 1
- `missing-ci-report-artifact`: 1
- `missing-codeowners`: 1
- `missing-contributing`: 1
- `missing-dependabot-config`: 1
- `missing-security-policy`: 1
- `release-workflow-without-guardrail`: 1
- `upload-artifact-v3`: 1
- `workflow-without-timeout`: 2

## Findings
- **medium** `checkout-v3-review` (ci-deprecation, confidence: medium) in `.github/workflows/ci.yml:7`
  - Signal: `- uses: actions/checkout@v3`
  - Why: Older checkout major versions can lag runtime/security maintenance.
  - Fix: Upgrade to actions/checkout@v4 and verify submodule/LFS/token behavior if used.
  - Fingerprint: `9bc5f341bd295f0f`
- **high** `upload-artifact-v3` (ci-deprecation, confidence: high) in `.github/workflows/release.yml:8`
  - Signal: `- uses: actions/upload-artifact@v3`
  - Why: upload-artifact v3 is retired for new runs and can break CI/report publishing.
  - Fix: Upgrade to actions/upload-artifact@v4 and verify retention/name/path behavior.
  - Fingerprint: `165bac21a22f35c0`
- **high** `local-action-node16` (ci-runtime, confidence: high) in `action.yml:3`
  - Signal: `using: node16`
  - Why: Local JavaScript action metadata uses an obsolete Node runtime.
  - Fix: Move the local action to a supported Node runtime and test it in CI.
  - Fingerprint: `bb92f8f2eefc0bd5`
- **medium** `missing-codeowners` (repo-hygiene, confidence: high) in `.`
  - Signal: `missing file: CODEOWNERS`
  - Why: No CODEOWNERS file was found.
  - Fix: Add CODEOWNERS under root, .github/, or docs/ to make review ownership explicit.
  - Fingerprint: `d08d1f97df911d77`
- **medium** `missing-security-policy` (repo-hygiene, confidence: high) in `.`
  - Signal: `missing file: SECURITY.md`
  - Why: No SECURITY.md policy was found.
  - Fix: Add SECURITY.md with supported versions and vulnerability reporting instructions.
  - Fingerprint: `514f35b6d63100a0`
- **low** `missing-contributing` (repo-hygiene, confidence: high) in `.`
  - Signal: `missing file: CONTRIBUTING.md`
  - Why: No CONTRIBUTING.md guide was found.
  - Fix: Add a short contribution and local test guide.
  - Fingerprint: `d2a9f08b7de29c04`
- **low** `missing-changelog` (repo-hygiene, confidence: high) in `.`
  - Signal: `missing file: CHANGELOG.md or HISTORY.md or RELEASES.md`
  - Why: No changelog/release history file was found.
  - Fix: Add CHANGELOG.md or document where release notes live.
  - Fingerprint: `65562851b495353f`
- **low** `missing-dependabot-config` (dependency-hygiene, confidence: medium) in `.`
  - Signal: `missing dependency update config`
  - Why: No Dependabot/Renovate config was found.
  - Fix: Add Dependabot or Renovate config if dependency update automation is appropriate for this repo.
  - Fingerprint: `fccdb0e957df324f`
- **medium** `missing-ci-report-artifact` (ci-observability, confidence: medium) in `.github/workflows/ci.yml`
  - Signal: `test-like workflow without artifact upload or job summary`
  - Why: Test-heavy CI is harder to debug when reports disappear after failed runs.
  - Fix: Upload test reports/logs with actions/upload-artifact@v4 or write a concise $GITHUB_STEP_SUMMARY.
  - Fingerprint: `0cb754fbe218d594`
- **low** `workflow-without-timeout` (ci-cost, confidence: low) in `.github/workflows/ci.yml`
  - Signal: `workflow jobs without visible timeout-minutes`
  - Why: Jobs without timeouts can hang and waste runner minutes.
  - Fix: Add `timeout-minutes` to long-running or externally-dependent jobs.
  - Fingerprint: `3aa850d3fcaed552`
- **low** `artifact-upload-without-always` (ci-observability, confidence: medium) in `.github/workflows/release.yml`
  - Signal: `artifact upload step without visible if: always()`
  - Why: Report upload steps can be skipped when earlier test steps fail.
  - Fix: Use `if: always()` on report/artifact upload steps where safe.
  - Fingerprint: `65c7cbc7ba97b948`
- **low** `workflow-without-timeout` (ci-cost, confidence: low) in `.github/workflows/release.yml`
  - Signal: `workflow jobs without visible timeout-minutes`
  - Why: Jobs without timeouts can hang and waste runner minutes.
  - Fix: Add `timeout-minutes` to long-running or externally-dependent jobs.
  - Fingerprint: `eba64df60fb25983`
- **high** `release-workflow-without-guardrail` (release-safety, confidence: medium) in `.github/workflows/release.yml`
  - Signal: `release-like workflow without obvious manual/environment guardrail`
  - Why: Release/publish workflows are reputation-impacting and should have an explicit guardrail.
  - Fix: Add workflow_dispatch, protected environment approvals, or a documented confirmation gate.
  - Fingerprint: `45746ac904c916c2`

## Notes
- Read-only local scan; No GitHub API, token, network call, or source upload.
- Rules are conservative preflight signals, not compliance/security guarantees.
- Review findings before failing CI or sharing reports publicly.
