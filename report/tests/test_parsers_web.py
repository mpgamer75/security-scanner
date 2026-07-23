"""Tests for nuclei and nikto output parsing."""
import unittest

from report.parsers import nuclei, nikto
from report.models import Severity

NUCLEI = """[CVE-2021-44228] [http] [critical] https://10.0.0.5:8443/api
[apache-detect] [http] [info] http://10.0.0.5 [Apache/2.4.7]
[tomcat-manager-default-creds] [http] [high] http://10.0.0.5:8080/manager/html
[tls-version] [ssl] [info] 10.0.0.5:443

Some noise line that is not a finding
"""

NIKTO = """- Nikto v2.5.0
+ Target IP:          10.0.0.5
+ Target Port:        80
+ Server: Apache/2.4.7 (Ubuntu)
+ Retrieved x-powered-by header: PHP/5.5.9
+ /admin/: Admin login page/section found.
+ OSVDB-3268: /icons/: Directory indexing found.
+ /backup.sql: Database backup file found.
+ 7962 requests: 0 error(s) and 3 item(s) reported on remote host
+ End Time:           2025-01-01 (2 seconds)
"""


class TestNuclei(unittest.TestCase):
    def test_parses_four_findings(self):
        self.assertEqual(len(nuclei.parse(NUCLEI)), 4)

    def test_severity_mapping(self):
        findings = {f.template_id: f for f in nuclei.parse(NUCLEI)}
        self.assertEqual(findings["CVE-2021-44228"].severity, Severity.CRITICAL)
        self.assertEqual(findings["tomcat-manager-default-creds"].severity, Severity.HIGH)
        self.assertEqual(findings["apache-detect"].severity, Severity.INFO)

    def test_extracts_cve_from_template_id(self):
        findings = {f.template_id: f for f in nuclei.parse(NUCLEI)}
        self.assertIn("CVE-2021-44228", findings["CVE-2021-44228"].cves)

    def test_parses_host_and_port(self):
        findings = {f.template_id: f for f in nuclei.parse(NUCLEI)}
        log4j = findings["CVE-2021-44228"]
        self.assertEqual(log4j.host, "10.0.0.5")
        self.assertEqual(log4j.port, 8443)
        self.assertEqual(findings["apache-detect"].port, 80)

    def test_source_is_nuclei(self):
        self.assertTrue(all(f.source == "nuclei" for f in nuclei.parse(NUCLEI)))

    def test_empty(self):
        self.assertEqual(nuclei.parse(""), [])


class TestNikto(unittest.TestCase):
    def test_skips_banner_and_summary_lines(self):
        titles = [f.title for f in nikto.parse(NIKTO)]
        joined = " ".join(titles)
        self.assertNotIn("Target IP", joined)
        self.assertNotIn("Nikto v", joined)
        self.assertNotIn("requests:", joined)
        self.assertNotIn("End Time", joined)

    def test_finds_the_three_real_items(self):
        titles = [f.title for f in nikto.parse(NIKTO)]
        self.assertEqual(len(titles), 3)
        self.assertTrue(any("admin" in t.lower() for t in titles))
        self.assertTrue(any("backup" in t.lower() for t in titles))

    def test_source_is_nikto(self):
        self.assertTrue(all(f.source == "nikto" for f in nikto.parse(NIKTO)))

    def test_backup_file_is_at_least_low(self):
        backup = next(f for f in nikto.parse(NIKTO) if "backup" in f.title.lower())
        self.assertGreaterEqual(backup.severity, Severity.LOW)

    def test_empty(self):
        self.assertEqual(nikto.parse(""), [])


if __name__ == "__main__":
    unittest.main()
