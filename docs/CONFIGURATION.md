# Configuration

The scanner auto-loads `.repo-hygiene-preflight.json` or `repo-hygiene-preflight.json` from the repository root. You can also pass `--config path/to/config.json`.

```json
{
  "ignore_rules": ["workflow-without-timeout"],
  "only_rules": [],
  "ignore_paths": ["docs/generated/**", "vendor/**"],
  "severity_overrides": {
    "missing-contributing": "info"
  },
  "baseline_fingerprints": []
}
```

## Fields

- `ignore_rules`: rule ids to skip.
- `only_rules`: if non-empty, run only these rule ids.
- `ignore_paths`: glob patterns relative to repo root.
- `severity_overrides`: map of rule id to `info`, `low`, `medium`, or `high`.
- `baseline_fingerprints`: finding fingerprints to suppress until fixed.

CLI flags `--only-rule` and `--ignore-rule` can be repeated and are useful for focused local checks.

## Baseline file

`--write-baseline repo-hygiene-baseline.json` writes current finding fingerprints. Later runs can use `--baseline repo-hygiene-baseline.json`.

Baselines are intended for gradual adoption, not hiding new findings forever.
