#!/usr/bin/env python3
"""Local no-token GitHub repository hygiene / CI risk preflight."""
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

SEVERITY_ORDER = {"info": 0, "low": 1, "medium": 2, "high": 3}
SEVERITIES = tuple(SEVERITY_ORDER)
WORKFLOW_GLOBS = ("*.yml", "*.yaml")
DEFAULT_CONFIG_NAMES = (".repo-hygiene-preflight.json", "repo-hygiene-preflight.json")
IGNORED_DIRS = {".git", "node_modules", ".venv", "venv", "dist", "build", "__pycache__"}


@dataclass(frozen=True)
class Rule:
    id: str
    severity: str
    category: str
    why: str
    fix: str
    confidence: str = "medium"
    pattern: str | None = None


@dataclass(frozen=True)
class Finding:
    rule_id: str
    severity: str
    category: str
    file: str
    line: int
    signal: str
    why: str
    fix: str
    confidence: str
    fingerprint: str


RULES: list[Rule] = [
    Rule("upload-artifact-v3", "high", "ci-deprecation", "upload-artifact v3 is retired for new runs and can break CI/report publishing.", "Upgrade to actions/upload-artifact@v4 and verify retention/name/path behavior.", "high", r"uses\s*:\s*actions/upload-artifact@v3\b"),
    Rule("download-artifact-v3", "high", "ci-deprecation", "download-artifact v3 is retired alongside upload-artifact v3.", "Upgrade to actions/download-artifact@v4 and test artifact names/merge behavior.", "high", r"uses\s*:\s*actions/download-artifact@v3\b"),
    Rule("cache-v3-review", "medium", "ci-deprecation", "Older cache action majors should be reviewed before runtime/service changes bite CI.", "Plan upgrade to actions/cache@v4 and verify key/restore-key behavior.", "medium", r"uses\s*:\s*actions/cache@v3\b"),
    Rule("checkout-v3-review", "medium", "ci-deprecation", "Older checkout major versions can lag runtime/security maintenance.", "Upgrade to actions/checkout@v4 and verify submodule/LFS/token behavior if used.", "medium", r"uses\s*:\s*actions/checkout@v3\b"),
    Rule("setup-node-v3-review", "medium", "ci-deprecation", "Older setup-node major versions should be reviewed before runtime/cache behavior changes.", "Upgrade to actions/setup-node@v4 and verify cache/node-version behavior.", "medium", r"uses\s*:\s*actions/setup-node@v3\b"),
    Rule("local-action-node16", "high", "ci-runtime", "Local JavaScript action metadata uses an obsolete Node runtime.", "Move the local action to a supported Node runtime and test it in CI.", "high", r"(?:runs\.using|using)\s*:\s*[\"']?node16[\"']?"),
    Rule("workflow-write-all-permissions", "high", "ci-permissions", "Workflow uses broad write-all permissions, increasing blast radius if a token is exposed or a job is compromised.", "Replace write-all with least-privilege job/workflow permissions.", "medium", r"permissions\s*:\s*write-all\b"),
    Rule("workflow-contents-write", "medium", "ci-permissions", "contents: write can mutate repository contents and should be limited to jobs that need it.", "Scope contents: write to release/publish jobs and prefer contents: read elsewhere.", "medium", r"contents\s*:\s*write\b"),
    Rule("pull-request-target-review", "high", "ci-permissions", "pull_request_target runs with elevated context and is risky with untrusted fork code.", "Use pull_request when possible; if pull_request_target is needed, avoid checking out untrusted code and minimize permissions.", "medium", r"pull_request_target\s*:"),
    Rule("missing-codeowners", "medium", "repo-hygiene", "No CODEOWNERS file was found.", "Add CODEOWNERS under root, .github/, or docs/ to make review ownership explicit.", "high"),
    Rule("missing-security-policy", "medium", "repo-hygiene", "No SECURITY.md policy was found.", "Add SECURITY.md with supported versions and vulnerability reporting instructions.", "high"),
    Rule("missing-contributing", "low", "repo-hygiene", "No CONTRIBUTING.md guide was found.", "Add a short contribution and local test guide.", "high"),
    Rule("missing-changelog", "low", "repo-hygiene", "No changelog/release history file was found.", "Add CHANGELOG.md or document where release notes live.", "high"),
    Rule("missing-dependabot-config", "low", "dependency-hygiene", "No Dependabot/Renovate config was found.", "Add Dependabot or Renovate config if dependency update automation is appropriate for this repo.", "medium"),
    Rule("missing-ci-report-artifact", "medium", "ci-observability", "Test-heavy CI is harder to debug when reports disappear after failed runs.", "Upload test reports/logs with actions/upload-artifact@v4 or write a concise $GITHUB_STEP_SUMMARY.", "medium"),
    Rule("artifact-upload-without-always", "low", "ci-observability", "Report upload steps can be skipped when earlier test steps fail.", "Use `if: always()` on report/artifact upload steps where safe.", "medium"),
    Rule("release-workflow-without-guardrail", "high", "release-safety", "Release/publish workflows are reputation-impacting and should have an explicit guardrail.", "Add workflow_dispatch, protected environment approvals, or a documented confirmation gate.", "medium"),
    Rule("workflow-without-timeout", "low", "ci-cost", "Jobs without timeouts can hang and waste runner minutes.", "Add `timeout-minutes` to long-running or externally-dependent jobs.", "low"),
]
RULE_BY_ID = {rule.id: rule for rule in RULES}


def normalize_config(raw: dict[str, Any] | None) -> dict[str, Any]:
    raw = raw or {}
    return {
        "ignore_rules": list(raw.get("ignore_rules", [])),
        "only_rules": list(raw.get("only_rules", [])),
        "ignore_paths": list(raw.get("ignore_paths", [])),
        "severity_overrides": dict(raw.get("severity_overrides", {})),
        "baseline_fingerprints": list(raw.get("baseline_fingerprints", [])),
    }


def load_config(root: Path, explicit: str | None = None) -> tuple[dict[str, Any], Path | None]:
    candidates = [Path(explicit)] if explicit else [root / name for name in DEFAULT_CONFIG_NAMES]
    for candidate in candidates:
        if candidate and candidate.exists():
            return normalize_config(json.loads(candidate.read_text(encoding="utf-8"))), candidate
    return normalize_config(None), None


def load_baseline(path: str | None) -> set[str]:
    if not path:
        return set()
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, list):
        return {str(item) for item in data}
    if isinstance(data, dict):
        if "baseline_fingerprints" in data:
            return {str(item) for item in data["baseline_fingerprints"]}
        if "findings" in data:
            return {str(item.get("fingerprint")) for item in data["findings"] if item.get("fingerprint")}
    raise ValueError("Baseline must be a list of fingerprints, a config with baseline_fingerprints, or a report with findings.")


def is_ignored_path(path: Path, root: Path, ignore_paths: Iterable[str] = ()) -> bool:
    try:
        rel_path = path.relative_to(root)
        parts = rel_path.parts
        rel_text = rel_path.as_posix()
    except ValueError:
        parts = path.parts
        rel_text = path.as_posix()
    if any(part in IGNORED_DIRS for part in parts):
        return True
    if path.name in {"report.md", "report.json"}:
        return True
    return any(fnmatch.fnmatch(rel_text, pattern) or fnmatch.fnmatch(path.name, pattern) for pattern in ignore_paths)


def rel(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def workflow_files(root: Path, config: dict[str, Any] | None = None) -> list[Path]:
    config = config or normalize_config(None)
    base = root / ".github" / "workflows"
    if not base.exists():
        return []
    files: list[Path] = []
    for glob in WORKFLOW_GLOBS:
        files.extend(p for p in base.rglob(glob) if p.is_file() and not is_ignored_path(p, root, config["ignore_paths"]))
    return sorted(set(files))


def action_metadata_files(root: Path, config: dict[str, Any] | None = None) -> list[Path]:
    config = config or normalize_config(None)
    names = {"action.yml", "action.yaml"}
    return sorted(p for p in root.rglob("action.y*ml") if p.is_file() and p.name in names and not is_ignored_path(p, root, config["ignore_paths"]))


def line_scan_files(root: Path, config: dict[str, Any] | None = None) -> list[Path]:
    config = config or normalize_config(None)
    md = [p for p in root.rglob("*.md") if p.is_file() and not is_ignored_path(p, root, config["ignore_paths"])]
    return sorted(set(workflow_files(root, config) + action_metadata_files(root, config) + md))


def find_file(root: Path, names: Iterable[str]) -> Path | None:
    wanted = {name.lower() for name in names}
    search_roots = [root, root / ".github", root / "docs"]
    for base in search_roots:
        if base.exists():
            for p in base.rglob("*"):
                if p.is_file() and p.name.lower() in wanted:
                    return p
    return None


def rule_enabled(rule_id: str, config: dict[str, Any]) -> bool:
    only_rules = set(config.get("only_rules", []))
    ignore_rules = set(config.get("ignore_rules", []))
    return (not only_rules or rule_id in only_rules) and rule_id not in ignore_rules


def make_finding(rule_id: str, root: Path, file: str, line: int, signal: str, config: dict[str, Any]) -> Finding:
    rule = RULE_BY_ID[rule_id]
    severity = config.get("severity_overrides", {}).get(rule_id, rule.severity)
    if severity not in SEVERITY_ORDER:
        raise ValueError(f"Invalid severity override for {rule_id}: {severity}")
    fingerprint_input = "|".join([rule_id, file, str(line), signal.strip()[:240]])
    fingerprint = hashlib.sha256(fingerprint_input.encode("utf-8")).hexdigest()[:16]
    return Finding(rule_id, severity, rule.category, file, line, signal.strip(), rule.why, rule.fix, rule.confidence, fingerprint)


def scan_line_rules(root: Path, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for path in line_scan_files(root, config):
        text = path.read_text(encoding="utf-8", errors="replace")
        for idx, line in enumerate(text.splitlines(), start=1):
            for rule in RULES:
                if not rule.pattern or not rule_enabled(rule.id, config):
                    continue
                if re.search(rule.pattern, line, flags=re.I):
                    findings.append(make_finding(rule.id, root, rel(path, root), idx, line, config))
    return findings


def scan_required_files(root: Path, config: dict[str, Any]) -> list[Finding]:
    checks = [
        ("missing-codeowners", ["CODEOWNERS"]),
        ("missing-security-policy", ["SECURITY.md"]),
        ("missing-contributing", ["CONTRIBUTING.md"]),
        ("missing-changelog", ["CHANGELOG.md", "HISTORY.md", "RELEASES.md"]),
    ]
    findings: list[Finding] = []
    for rule_id, names in checks:
        if rule_enabled(rule_id, config) and not find_file(root, names):
            findings.append(make_finding(rule_id, root, ".", 0, "missing file: " + " or ".join(names), config))
    if rule_enabled("missing-dependabot-config", config):
        has_dependabot = (root / ".github" / "dependabot.yml").exists() or (root / ".github" / "dependabot.yaml").exists()
        has_renovate = any((root / name).exists() for name in ("renovate.json", ".renovaterc", ".renovaterc.json")) or (root / ".github" / "renovate.json").exists()
        if not (has_dependabot or has_renovate):
            findings.append(make_finding("missing-dependabot-config", root, ".", 0, "missing dependency update config", config))
    return findings


def scan_ci_report_hygiene(root: Path, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    for path in workflow_files(root, config):
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        file = rel(path, root)
        testish = bool(re.search(r"\b(pytest|npm test|pnpm test|yarn test|go test|cargo test|vitest|playwright test)\b", lower))
        has_report_upload = "actions/upload-artifact" in lower or "github_step_summary" in lower or "$github_step_summary" in lower
        if rule_enabled("missing-ci-report-artifact", config) and testish and not has_report_upload:
            findings.append(make_finding("missing-ci-report-artifact", root, file, 0, "test-like workflow without artifact upload or job summary", config))
        if rule_enabled("artifact-upload-without-always", config) and "actions/upload-artifact" in lower and "if: always()" not in lower:
            findings.append(make_finding("artifact-upload-without-always", root, file, 0, "artifact upload step without visible if: always()", config))
        if rule_enabled("workflow-without-timeout", config) and re.search(r"^\s*jobs\s*:", text, flags=re.M) and "timeout-minutes" not in lower:
            findings.append(make_finding("workflow-without-timeout", root, file, 0, "workflow jobs without visible timeout-minutes", config))
    return findings


def scan_release_guardrails(root: Path, config: dict[str, Any]) -> list[Finding]:
    findings: list[Finding] = []
    if not rule_enabled("release-workflow-without-guardrail", config):
        return findings
    for path in workflow_files(root, config):
        text = path.read_text(encoding="utf-8", errors="replace")
        lower = text.lower()
        file = rel(path, root)
        if not any(word in path.name.lower() for word in ("release", "publish", "deploy")) and not any(token in lower for token in ("pypi", "npm publish", "gh release", "docker/login-action")):
            continue
        has_manual = "workflow_dispatch" in lower
        has_env = re.search(r"^\s*environment\s*:", text, flags=re.M) is not None
        has_confirmation = re.search(r"confirm|approval|review", lower) is not None
        if not (has_manual or has_env or has_confirmation):
            findings.append(make_finding("release-workflow-without-guardrail", root, file, 0, "release-like workflow without obvious manual/environment guardrail", config))
    return findings


def scan(root: Path, config_path: str | None = None, baseline_path: str | None = None) -> dict[str, Any]:
    root = root.resolve()
    config, loaded_config_path = load_config(root, config_path)
    baseline = set(config.get("baseline_fingerprints", [])) | load_baseline(baseline_path)
    findings = scan_line_rules(root, config) + scan_required_files(root, config) + scan_ci_report_hygiene(root, config) + scan_release_guardrails(root, config)
    if baseline:
        findings = [finding for finding in findings if finding.fingerprint not in baseline]
    return {
        "tool": "repo-hygiene-ci-risk-preflight",
        "version": "0.1.0",
        "root": str(root),
        "config": str(loaded_config_path) if loaded_config_path else None,
        "scanned_workflows": len(workflow_files(root, config)),
        "scanned_files": len(line_scan_files(root, config)),
        "active_rules": [rule.id for rule in RULES if rule_enabled(rule.id, config)],
        "finding_count": len(findings),
        "summary_by_severity": summary(findings, "severity"),
        "summary_by_category": summary(findings, "category"),
        "summary_by_rule": summary(findings, "rule_id"),
        "findings": [asdict(f) for f in findings],
        "notes": [
            "Read-only local scan; No GitHub API, token, network call, or source upload.",
            "Rules are conservative preflight signals, not compliance/security guarantees.",
            "Review findings before failing CI or sharing reports publicly.",
        ],
    }


def summary(findings: list[Finding], field: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for finding in findings:
        key = getattr(finding, field)
        out[key] = out.get(key, 0) + 1
    return dict(sorted(out.items()))


def filtered_report(report: dict[str, Any], min_severity: str | None) -> dict[str, Any]:
    if not min_severity:
        return report
    minimum = SEVERITY_ORDER[min_severity]
    findings = [Finding(**item) for item in report["findings"]]
    kept = [f for f in findings if SEVERITY_ORDER.get(f.severity, 0) >= minimum]
    notes = list(report["notes"])
    notes.append(f"Filtered findings below {min_severity} severity.")
    return {**report, "finding_count": len(kept), "summary_by_severity": summary(kept, "severity"), "summary_by_category": summary(kept, "category"), "summary_by_rule": summary(kept, "rule_id"), "findings": [asdict(f) for f in kept], "notes": notes}


def render_markdown(report: dict[str, Any]) -> str:
    lines = ["# Repository Hygiene / CI Risk Preflight", "", f"Scanned workflows: {report['scanned_workflows']}", f"Scanned files: {report['scanned_files']}", f"Active rules: {len(report.get('active_rules', []))}", f"Findings: {report['finding_count']}", ""]
    if report["summary_by_severity"]:
        lines.append("## Summary by severity")
        for severity, count in report["summary_by_severity"].items():
            lines.append(f"- **{severity}**: {count}")
        lines.append("")
    if report.get("summary_by_category"):
        lines.append("## Summary by category")
        for category, count in report["summary_by_category"].items():
            lines.append(f"- `{category}`: {count}")
        lines.append("")
    if report["summary_by_rule"]:
        lines.append("## Summary by rule")
        for rule_id, count in report["summary_by_rule"].items():
            lines.append(f"- `{rule_id}`: {count}")
        lines.append("")
    if report["findings"]:
        lines.append("## Findings")
        for item in report["findings"]:
            loc = item["file"] if item["line"] == 0 else f"{item['file']}:{item['line']}"
            lines.append(f"- **{item['severity']}** `{item['rule_id']}` ({item['category']}, confidence: {item['confidence']}) in `{loc}`")
            lines.append(f"  - Signal: `{item['signal']}`")
            lines.append(f"  - Why: {item['why']}")
            lines.append(f"  - Fix: {item['fix']}")
            lines.append(f"  - Fingerprint: `{item['fingerprint']}`")
    else:
        lines.append("No repository hygiene risks found by the current rule set.")
    lines.extend(["", "## Notes"])
    for note in report["notes"]:
        lines.append(f"- {note}")
    return "\n".join(lines) + "\n"


def render_annotations(report: dict[str, Any]) -> str:
    level = {"high": "error", "medium": "warning", "low": "notice", "info": "notice"}
    lines: list[str] = []
    for item in report["findings"]:
        file = item["file"] if item["file"] != "." else "README.md"
        line = max(int(item["line"]), 1)
        title = f"{item['rule_id']} ({item['severity']})"
        message = f"{item['why']} Fix: {item['fix']} Fingerprint: {item['fingerprint']}"
        message = message.replace("\n", " ").replace("%", "%25").replace("\r", "%0D").replace("\n", "%0A")
        lines.append(f"::{level.get(item['severity'], 'notice')} file={file},line={line},title={title}::{message}")
    return "\n".join(lines) + ("\n" if lines else "")


def render_rules_json() -> str:
    return json.dumps([asdict(rule) for rule in RULES], indent=2) + "\n"


def render_rules_markdown() -> str:
    lines = ["# Repo Hygiene CI Risk Preflight rules", ""]
    for rule in RULES:
        lines.append(f"## `{rule.id}`")
        lines.append(f"- Severity: `{rule.severity}`")
        lines.append(f"- Category: `{rule.category}`")
        lines.append(f"- Confidence: `{rule.confidence}`")
        lines.append(f"- Why: {rule.why}")
        lines.append(f"- Fix: {rule.fix}")
        if rule.pattern:
            lines.append(f"- Pattern: `{rule.pattern}`")
        lines.append("")
    return "\n".join(lines)


def write_baseline(report: dict[str, Any], path: str) -> None:
    data = {
        "tool": report["tool"],
        "baseline_fingerprints": [item["fingerprint"] for item in report["findings"]],
        "finding_count": report["finding_count"],
    }
    Path(path).write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def should_fail(report: dict[str, Any], threshold: str) -> bool:
    minimum = SEVERITY_ORDER[threshold]
    return any(SEVERITY_ORDER.get(item["severity"], 0) >= minimum for item in report["findings"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Scan a checked-out GitHub repo for hygiene and CI risk signals.")
    parser.add_argument("path", nargs="?", default=".", help="Repository root to scan")
    parser.add_argument("--format", choices=["markdown", "json", "annotations"], default="markdown")
    parser.add_argument("--output", "-o", help="Write report to file")
    parser.add_argument("--config", help="Path to JSON config file")
    parser.add_argument("--baseline", help="Path to baseline JSON/report whose fingerprints should be suppressed")
    parser.add_argument("--write-baseline", help="Write current findings as a baseline JSON file")
    parser.add_argument("--min-severity", choices=["low", "medium", "high"], help="Only include findings at or above this severity")
    parser.add_argument("--fail-on-severity", choices=["low", "medium", "high"], help="Exit 1 if findings at or above this severity remain after filters")
    parser.add_argument("--only-rule", action="append", default=[], help="Only run a rule id; repeatable")
    parser.add_argument("--ignore-rule", action="append", default=[], help="Ignore a rule id; repeatable")
    parser.add_argument("--list-rules", action="store_true", help="List active rule inventory and exit")
    args = parser.parse_args(argv)

    if args.list_rules:
        output = render_rules_json() if args.format == "json" else render_rules_markdown()
        if args.output:
            Path(args.output).write_text(output, encoding="utf-8")
        else:
            print(output, end="")
        return 0

    root = Path(args.path)
    config, config_path = load_config(root.resolve(), args.config)
    config["only_rules"].extend(args.only_rule)
    config["ignore_rules"].extend(args.ignore_rule)
    unknown = sorted((set(config["only_rules"]) | set(config["ignore_rules"]) | set(config["severity_overrides"])) - set(RULE_BY_ID))
    if unknown:
        parser.error("Unknown rule id(s): " + ", ".join(unknown))

    report = scan(root, str(config_path) if config_path else None, args.baseline)
    # Re-apply CLI-only rule config when no config file was used by scanning through an in-memory temporary path is overkill;
    # run direct scan helpers for CLI-only rule filters.
    if args.only_rule or args.ignore_rule or config["severity_overrides"] or config["ignore_paths"]:
        root_resolved = root.resolve()
        baseline = set(config.get("baseline_fingerprints", [])) | load_baseline(args.baseline)
        findings = scan_line_rules(root_resolved, config) + scan_required_files(root_resolved, config) + scan_ci_report_hygiene(root_resolved, config) + scan_release_guardrails(root_resolved, config)
        if baseline:
            findings = [finding for finding in findings if finding.fingerprint not in baseline]
        report = {**report, "config": str(config_path) if config_path else None, "scanned_workflows": len(workflow_files(root_resolved, config)), "scanned_files": len(line_scan_files(root_resolved, config)), "active_rules": [rule.id for rule in RULES if rule_enabled(rule.id, config)], "finding_count": len(findings), "summary_by_severity": summary(findings, "severity"), "summary_by_category": summary(findings, "category"), "summary_by_rule": summary(findings, "rule_id"), "findings": [asdict(f) for f in findings]}

    report = filtered_report(report, args.min_severity)
    if args.write_baseline:
        write_baseline(report, args.write_baseline)

    if args.format == "json":
        output = json.dumps(report, indent=2) + "\n"
    elif args.format == "annotations":
        output = render_annotations(report)
    else:
        output = render_markdown(report)
    if args.output:
        Path(args.output).write_text(output, encoding="utf-8")
    else:
        print(output, end="")
    return 1 if args.fail_on_severity and should_fail(report, args.fail_on_severity) else 0


if __name__ == "__main__":
    raise SystemExit(main())
