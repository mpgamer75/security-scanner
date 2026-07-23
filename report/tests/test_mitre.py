"""Tests for the expanded MITRE ATT&CK mapping, coverage, and Navigator export."""
import json
import unittest

from report import mitre
from report.models import Finding, Severity


class TestTechniqueRecord(unittest.TestCase):
    def test_known_has_tactic_and_name(self):
        rec = mitre.technique_record("T1595.002")
        self.assertEqual(rec["tactic"], "TA0043")
        self.assertIn("Vulnerability", rec["name"])

    def test_unknown_returns_none(self):
        self.assertIsNone(mitre.technique_record("T9999"))

    def test_url_builds_sub_technique_path(self):
        self.assertEqual(
            mitre.technique_url("T1595.002"),
            "https://attack.mitre.org/techniques/T1595/002",
        )


class TestTechniquesForFinding(unittest.TestCase):
    def test_recon_source_maps_to_active_scanning(self):
        f = Finding(title="x", source="nuclei", severity=Severity.INFO)
        ids = [t["technique"] for t in mitre.techniques_for_finding(f)]
        self.assertIn("T1595.002", ids)

    def test_web_critical_indicates_exploit_public_facing(self):
        f = Finding(title="x", source="nuclei", severity=Severity.CRITICAL, cves=["CVE-2021-44228"])
        ids = [t["technique"] for t in mitre.techniques_for_finding(f)]
        self.assertIn("T1190", ids)

    def test_network_vuln_indicates_remote_service_exploit(self):
        f = Finding(title="smb-vuln-ms17-010", source="nmap-nse",
                    severity=Severity.CRITICAL, cves=["CVE-2017-0143"], port=445)
        ids = [t["technique"] for t in mitre.techniques_for_finding(f)]
        self.assertIn("T1210", ids)

    def test_info_finding_has_no_indicated_initial_access(self):
        f = Finding(title="x", source="nuclei", severity=Severity.INFO)
        ids = [t["technique"] for t in mitre.techniques_for_finding(f)]
        self.assertNotIn("T1190", ids)


class TestTagFindings(unittest.TestCase):
    def test_all_findings_tagged(self):
        findings = [
            Finding(title="a", source="nuclei", severity=Severity.CRITICAL, cves=["CVE-2021-44228"]),
            Finding(title="b", source="nmap-nse", severity=Severity.INFO),
        ]
        mitre.tag_findings(findings)
        self.assertTrue(all(f.mitre for f in findings))


class TestCoverage(unittest.TestCase):
    def test_groups_by_tactic_with_counts(self):
        findings = [
            Finding(title="a", source="nuclei", severity=Severity.CRITICAL, cves=["CVE-2021-44228"]),
            Finding(title="b", source="nmap-nse", severity=Severity.INFO),
        ]
        mitre.tag_findings(findings)
        cov = mitre.coverage(findings)
        self.assertIn("TA0043", cov)
        self.assertGreaterEqual(cov["TA0043"]["techniques"]["T1595.002"]["count"], 2)
        # the log4shell finding also indicates Initial Access
        self.assertIn("TA0001", cov)

    def test_empty(self):
        self.assertEqual(mitre.coverage([]), {})


class TestNavigatorLayer(unittest.TestCase):
    def test_valid_layer_with_techniques(self):
        findings = [Finding(title="a", source="nuclei", severity=Severity.CRITICAL, cves=["CVE-2021-44228"])]
        mitre.tag_findings(findings)
        layer = mitre.navigator_layer(findings)
        json.dumps(layer)  # must be serializable
        self.assertEqual(layer["domain"], "enterprise-attack")
        ids = [t["techniqueID"] for t in layer["techniques"]]
        self.assertIn("T1595.002", ids)
        self.assertIn("T1190", ids)

    def test_scores_reflect_counts(self):
        findings = [Finding(title=str(i), source="nuclei", severity=Severity.INFO) for i in range(3)]
        mitre.tag_findings(findings)
        layer = mitre.navigator_layer(findings)
        rec = next(t for t in layer["techniques"] if t["techniqueID"] == "T1595.002")
        self.assertEqual(rec["score"], 3)


if __name__ == "__main__":
    unittest.main()
