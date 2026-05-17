# PyPI production publishing plan — repo-hygiene-ci-risk-preflight

Status: local preparation only. Do not push workflow, create PyPI project/publisher, dispatch workflow, or publish without explicit scoped approval.

## Recommended path

Use PyPI Trusted Publishing via GitHub Actions, matching the existing suite workflow pattern.

## Required live steps after approval

1. Push `.github/workflows/publish.yml` to `vasiliy0/repo-hygiene-ci-risk-preflight`.
2. Configure PyPI Trusted Publisher for project `repo-hygiene-ci-risk-preflight` with:
   - owner: `vasiliy0`
   - repository: `repo-hygiene-ci-risk-preflight`
   - workflow: `publish.yml`
   - environment: `pypi`
3. Optionally configure TestPyPI Trusted Publisher with environment `testpypi` for a validation upload.
4. Dispatch the workflow with `target=pypi` only after the publisher exists.
5. Verify PyPI JSON/project page and record the release in state.

## Not included

No API tokens, passwords, billing, payout, Sponsors, marketplace listing, DMs, ads, or extra outreach.
