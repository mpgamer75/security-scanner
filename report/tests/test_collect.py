"""Integration test: read a redteam_*/ output tree into an Assessment."""
import os
import shutil
import tempfile
import unittest

from report import collect, severity
from report.models import Severity

PORTS = """Nmap scan report for 10.0.0.5
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
445/tcp   open  microsoft-ds
8443/tcp  open  https-alt
"""

SERVICES = """Nmap scan report for 10.0.0.5
PORT      STATE SERVICE       VERSION
22/tcp    open  ssh           OpenSSH 6.6.1p1 Ubuntu
80/tcp    open  http          Apache httpd 2.4.7
445/tcp   open  microsoft-ds  Samba smbd 4.3.11
"""

VULNS = """Nmap scan report for 10.0.0.5
Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|_    Risk factor: HIGH
"""

NUCLEI = """[CVE-2021-44228] [http] [critical] https://10.0.0.5:8443/api
[apache-detect] [http] [info] http://10.0.0.5 [Apache/2.4.7]
"""

NIKTO = """+ Server: Apache/2.4.7
+ /backup.sql: Database backup file found.
"""


def _write(base, rel, content):
    path = os.path.join(base, *rel.split("/"))
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(content)


class TestCollect(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        _write(self.tmp, "network/nmap_ports.txt", PORTS)
        _write(self.tmp, "network/nmap_services.txt", SERVICES)
        _write(self.tmp, "network/nmap_vulns.txt", VULNS)
        _write(self.tmp, "web/nuclei.txt", NUCLEI)
        _write(self.tmp, "web/nikto.txt", NIKTO)
        _write(self.tmp, "web/wafw00f.txt",
               "[+] The site https://x is behind Cloudflare (Cloudflare Inc.) WAF.")
        _write(self.tmp, "osint/all_subdomains.txt",
               "www.example.com\nmail.example.com\napi.example.com\n")
        _write(self.tmp, "osint/emails.txt", "admin@example.com\ninfo@example.com\n")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_findings_include_known_critical(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        self.assertTrue(any("CVE-2017-0143" in f.cves for f in assessment.findings))
        self.assertTrue(any("CVE-2021-44228" in f.cves for f in assessment.findings))

    def test_services_grouped_into_host(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        ports = sorted(s.port for h in assessment.hosts for s in h.services)
        self.assertEqual(ports, [22, 80, 445, 8443])

    def test_service_version_merged_from_sv_scan(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        svc22 = next(s for h in assessment.hosts for s in h.services if s.port == 22)
        self.assertIn("OpenSSH", svc22.version or "")

    def test_waf_detected(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        self.assertIn("Cloudflare", assessment.assets.waf or "")

    def test_subdomains_and_emails(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        self.assertEqual(len(assessment.assets.subdomains), 3)
        self.assertEqual(len(assessment.assets.emails), 2)

    def test_findings_are_mitre_tagged(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        self.assertTrue(all(f.mitre for f in assessment.findings))

    def test_risk_reflects_critical(self):
        assessment = collect.build_assessment(self.tmp, target="10.0.0.5")
        self.assertGreaterEqual(severity.risk_score(assessment.findings), 60)

    def test_missing_directory_is_empty_not_error(self):
        assessment = collect.build_assessment(os.path.join(self.tmp, "nope"), target="x")
        self.assertEqual(assessment.findings, [])
        self.assertEqual(assessment.hosts, [])


if __name__ == "__main__":
    unittest.main()
