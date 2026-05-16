# GitHub Action wrapper draft

This is a local design artifact, not a published action.

## Composite action shape

```yaml
name: Repository Hygiene CI Risk Preflight
description: Local no-token scan for repo hygiene and CI risk signals
inputs:
  path:
    description: Repository path
    default: .
  min-severity:
    description: Minimum severity to include
    required: false
  fail-on-severity:
    description: Fail when findings at or above this severity exist
    required: false
runs:
  using: composite
  steps:
    - shell: bash
      run: |
        python -m pip install repo-hygiene-ci-risk-preflight
        args=("${{ inputs.path }}" --format markdown --output repo-hygiene-report.md)
        if [ -n "${{ inputs.min-severity }}" ]; then args+=(--min-severity "${{ inputs.min-severity }}"); fi
        if [ -n "${{ inputs.fail-on-severity }}" ]; then args+=(--fail-on-severity "${{ inputs.fail-on-severity }}"); fi
        repo-hygiene-preflight "${args[@]}"
```

## Preferred initial distribution

Start with documented workflow snippets. Publish a dedicated GitHub Action only after the package has stable install behavior and users ask for one-step integration.
