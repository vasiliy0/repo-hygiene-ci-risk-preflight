# PyPI/TestPyPI readiness

Status: local v0.1.0 development artifact. No package registry upload has been performed.

## Scope

- Package: `repo-hygiene-ci-risk-preflight`
- Console script: `repo-hygiene-preflight`
- Distribution target when approved: TestPyPI first
- Production PyPI: separate explicit approval required

## Local checks required before approval request

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile scanner.py src/repo_hygiene_ci_risk_preflight/*.py
python3 scanner.py examples --format markdown --output examples/report.md
python3 scanner.py examples --format json --output examples/report.json
python3 -m build
python3 -m twine check dist/*
```

If system `twine` is too old for current metadata, use the already-created temporary local packaging venv if available.

## Approval needed before external actions

Ask before:

- GitHub push
- TestPyPI upload
- production PyPI upload
- GitHub release/tag
- marketplace/GitHub App/payment/outreach steps

## Trusted Publishing plan

A future `publish.yml` should support `workflow_dispatch` with `target=testpypi` and `target=pypi`, protected by separate environments. Dispatch only `target=testpypi` unless production PyPI is explicitly approved.
