# Repository Hygiene / CI Risk Preflight v0.1.1

Agent/CI integration release.

## Added

- Versioned JSON report contract fields: `schema_version`, `tool_version`, `status`, `summary`, and `metadata`.
- JSON schema at `schemas/report.schema.json`.
- AI-agent integration guide at `docs/AGENT_INTEGRATION.md`.
- Automation-safe `--quiet` and `--no-color` flags.
- Marketplace-ready composite `action.yml` for local/no-token scans.

## Compatibility

Existing JSON fields, Markdown output, annotations, config, baselines, and severity gates remain available.
