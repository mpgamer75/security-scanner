"""Tests for the severity / CVE / risk model that replaces substring counting."""
import unittest

from report.models import Severity, Finding
from report import severity


class TestSeverityEnum(unittest.TestCase):
    def test_ordering(self):
        self.assertTrue(
            Severity.CRITICAL > Severity.HIGH > Severity.MEDIUM > Severity.LOW > Severity.INFO
        )

    def test_from_str_plain(self):
        self.assertEqual(Severity.from_str("critical"), Severity.CRITICAL)
        self.assertEqual(Severity.from_str("HIGH"), Severity.HIGH)

    def test_from_str_bracketed_nuclei_tag(self):
        self.assertEqual(Severity.from_str("[medium]"), Severity.MEDIUM)

    def test_from_str_unknown_defaults_to_info(self):
        self.assertEqual(Severity.from_str("banana"), Severity.INFO)
        self.assertEqual(Severity.from_str(""), Severity.INFO)
        self.assertEqual(Severity.from_str(None), Severity.INFO)

    def test_label_is_lowercase_name(self):
        self.assertEqual(Severity.CRITICAL.label, "critical")


class TestCveExtraction(unittest.TestCase):
    def test_extracts_and_uppercases(self):
        self.assertEqual(severity.extract_cves("hit cve-2021-44228 here"), ["CVE-2021-44228"])

    def test_dedupes_preserving_first_seen_order(self):
        text = "CVE-2017-0144 then CVE-2021-44228 then cve-2017-0144 again"
        self.assertEqual(
            severity.extract_cves(text), ["CVE-2017-0144", "CVE-2021-44228"]
        )

    def test_no_cve_returns_empty(self):
        self.assertEqual(severity.extract_cves("nothing here"), [])

    def test_handles_long_cve_ids(self):
        self.assertEqual(severity.extract_cves("CVE-2024-1234567"), ["CVE-2024-1234567"])


class TestCvssBanding(unittest.TestCase):
    def test_bands(self):
        self.assertEqual(severity.severity_from_cvss(9.8), Severity.CRITICAL)
        self.assertEqual(severity.severity_from_cvss(9.0), Severity.CRITICAL)
        self.assertEqual(severity.severity_from_cvss(7.5), Severity.HIGH)
        self.assertEqual(severity.severity_from_cvss(4.0), Severity.MEDIUM)
        self.assertEqual(severity.severity_from_cvss(0.1), Severity.LOW)
        self.assertEqual(severity.severity_from_cvss(0.0), Severity.INFO)

    def test_none_is_info(self):
        self.assertEqual(severity.severity_from_cvss(None), Severity.INFO)


class TestKnownCveLookup(unittest.TestCase):
    def test_eternalblue_is_critical(self):
        self.assertEqual(severity.severity_for_cve("CVE-2017-0144"), Severity.CRITICAL)

    def test_log4shell_is_critical(self):
        self.assertEqual(severity.severity_for_cve("CVE-2021-44228"), Severity.CRITICAL)

    def test_unknown_cve_returns_none(self):
        self.assertIsNone(severity.severity_for_cve("CVE-1999-0001"))


class TestRiskScore(unittest.TestCase):
    def test_empty_is_zero(self):
        self.assertEqual(severity.risk_score([]), 0)

    def test_single_critical_is_high(self):
        score = severity.risk_score([Finding(title="x", severity=Severity.CRITICAL)])
        self.assertGreaterEqual(score, 60)
        self.assertLessEqual(score, 100)

    def test_info_only_stays_low(self):
        findings = [Finding(title="x", severity=Severity.INFO) for _ in range(20)]
        self.assertLess(severity.risk_score(findings), 20)

    def test_more_criticals_scores_higher_but_capped(self):
        one = severity.risk_score([Finding(title="a", severity=Severity.CRITICAL)])
        many = severity.risk_score(
            [Finding(title=str(i), severity=Severity.CRITICAL) for i in range(50)]
        )
        self.assertGreaterEqual(many, one)
        self.assertLessEqual(many, 100)


class TestDedupe(unittest.TestCase):
    def test_same_host_port_cve_from_two_tools_collapses(self):
        f1 = Finding(
            title="MS17-010", host="10.0.0.5", port=445,
            cves=["CVE-2017-0144"], severity=Severity.CRITICAL, source="nmap-nse",
        )
        f2 = Finding(
            title="MS17-010 SMB", host="10.0.0.5", port=445,
            cves=["CVE-2017-0144"], severity=Severity.CRITICAL, source="nuclei",
        )
        deduped = severity.dedupe([f1, f2])
        self.assertEqual(len(deduped), 1)

    def test_different_ports_not_merged(self):
        f1 = Finding(title="x", host="10.0.0.5", port=445, severity=Severity.HIGH)
        f2 = Finding(title="x", host="10.0.0.5", port=139, severity=Severity.HIGH)
        self.assertEqual(len(severity.dedupe([f1, f2])), 2)

    def test_dedupe_keeps_highest_severity(self):
        f1 = Finding(title="x", host="h", port=1, cves=["CVE-2020-0001"], severity=Severity.LOW)
        f2 = Finding(title="x", host="h", port=1, cves=["CVE-2020-0001"], severity=Severity.CRITICAL)
        out = severity.dedupe([f1, f2])
        self.assertEqual(len(out), 1)
        self.assertEqual(out[0].severity, Severity.CRITICAL)


if __name__ == "__main__":
    unittest.main()
