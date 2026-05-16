from pathlib import Path
import importlib.util
import json
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("scanner", ROOT / "scanner.py")
scanner = importlib.util.module_from_spec(spec)
sys.modules["scanner"] = scanner
spec.loader.exec_module(scanner)

class TestRepoHygieneScanner(unittest.TestCase):
    def test_example_finds_ci_and_hygiene_risks(self):
        report = scanner.scan(ROOT / "examples")
        ids = {item["rule_id"] for item in report["findings"]}
        self.assertIn("upload-artifact-v3", ids)
        self.assertIn("local-action-node16", ids)
        self.assertIn("missing-codeowners", ids)
        self.assertIn("missing-security-policy", ids)
        self.assertIn("missing-ci-report-artifact", ids)
        self.assertIn("release-workflow-without-guardrail", ids)

    def test_markdown_mentions_no_token_privacy(self):
        text = scanner.render_markdown(scanner.scan(ROOT / "examples"))
        self.assertIn("Repository Hygiene / CI Risk Preflight", text)
        self.assertIn("No GitHub API, token", text)
        self.assertIn("Summary by severity", text)

    def test_json_output_and_fail_on_severity(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "report.json"
            code = scanner.main([str(ROOT / "examples"), "--format", "json", "--output", str(output), "--fail-on-severity", "high"])
            self.assertEqual(code, 1)
            data = json.loads(output.read_text())
            self.assertGreaterEqual(data["summary_by_severity"]["high"], 1)

    def test_min_severity_filters_low_findings(self):
        report = scanner.filtered_report(scanner.scan(ROOT / "examples"), "medium")
        severities = {item["severity"] for item in report["findings"]}
        self.assertNotIn("low", severities)
        self.assertIn("Filtered findings below medium severity.", report["notes"])

    def test_list_rules_outputs_active_inventory(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "rules.json"
            code = scanner.main(["--list-rules", "--format", "json", "--output", str(output)])
            self.assertEqual(code, 0)
            rules = json.loads(output.read_text())
            ids = {rule["id"] for rule in rules}
            self.assertIn("workflow-write-all-permissions", ids)
            self.assertIn("missing-dependabot-config", ids)

    def test_only_and_ignore_rule_filters(self):
        report = scanner.scan(ROOT / "examples")
        self.assertIn("upload-artifact-v3", {item["rule_id"] for item in report["findings"]})
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "only.json"
            code = scanner.main([str(ROOT / "examples"), "--format", "json", "--only-rule", "missing-codeowners", "--output", str(output)])
            self.assertEqual(code, 0)
            data = json.loads(output.read_text())
            self.assertEqual({item["rule_id"] for item in data["findings"]}, {"missing-codeowners"})

    def test_config_severity_override_and_baseline(self):
        with tempfile.TemporaryDirectory() as tmp:
            config = Path(tmp) / "config.json"
            config.write_text(json.dumps({"severity_overrides": {"missing-codeowners": "high"}, "ignore_rules": ["missing-dependabot-config"]}))
            output = Path(tmp) / "report.json"
            code = scanner.main([str(ROOT / "examples"), "--config", str(config), "--format", "json", "--output", str(output), "--write-baseline", str(Path(tmp) / "baseline.json")])
            self.assertEqual(code, 0)
            data = json.loads(output.read_text())
            by_rule = {item["rule_id"]: item for item in data["findings"]}
            self.assertEqual(by_rule["missing-codeowners"]["severity"], "high")
            self.assertNotIn("missing-dependabot-config", by_rule)
            baseline = Path(tmp) / "baseline.json"
            output2 = Path(tmp) / "after-baseline.json"
            scanner.main([str(ROOT / "examples"), "--config", str(config), "--baseline", str(baseline), "--format", "json", "--output", str(output2)])
            self.assertEqual(json.loads(output2.read_text())["finding_count"], 0)

    def test_annotations_output(self):
        text = scanner.render_annotations(scanner.filtered_report(scanner.scan(ROOT / "examples"), "high"))
        self.assertIn("::error", text)
        self.assertIn("upload-artifact-v3", text)

if __name__ == "__main__":
    unittest.main()
