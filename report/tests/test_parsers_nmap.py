"""Tests for nmap output parsing (ports, service/version, NSE vuln scripts)."""
import unittest

from report.parsers import nmap
from report.models import Severity

PORTS = """Starting Nmap 7.94 ( https://nmap.org )
Nmap scan report for scanme.nmap.org (45.33.32.156)
Host is up (0.089s latency).
Not shown: 996 closed tcp ports (reset)
PORT      STATE SERVICE
22/tcp    open  ssh
80/tcp    open  http
9929/tcp  open  nping-echo
31337/tcp open  Elite
443/tcp   closed https
"""

SERVICES = """Nmap scan report for 10.0.0.5
PORT      STATE SERVICE       VERSION
22/tcp    open  ssh           OpenSSH 6.6.1p1 Ubuntu 2ubuntu2.13 (Ubuntu Linux; protocol 2.0)
80/tcp    open  http          Apache httpd 2.4.7 ((Ubuntu))
443/tcp   open  ssl/http      nginx 1.18.0
"""

VULNS = """Nmap scan report for 10.0.0.5
Host is up (0.0010s latency).
PORT    STATE SERVICE
445/tcp open  microsoft-ds
Host script results:
| smb-vuln-ms17-010:
|   VULNERABLE:
|   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
|     State: VULNERABLE
|     IDs:  CVE:CVE-2017-0143
|     Risk factor: HIGH
|_    https://technet.microsoft.com/en-us/library/security/ms17-010.aspx
| ssl-poodle:
|   VULNERABLE:
|   SSL POODLE information leak
|     State: VULNERABLE
|     IDs:  CVE:CVE-2014-3566
|_    Risk factor: MEDIUM
"""

CLEAN = """Nmap scan report for 10.0.0.9
PORT   STATE SERVICE
22/tcp open  ssh
"""


class TestNmapPorts(unittest.TestCase):
    def test_parses_only_open_ports(self):
        services = nmap.parse_ports(PORTS)
        self.assertEqual(sorted(s.port for s in services), [22, 80, 9929, 31337])

    def test_excludes_closed_ports(self):
        services = nmap.parse_ports(PORTS)
        self.assertNotIn(443, [s.port for s in services])

    def test_captures_name_state_proto(self):
        services = nmap.parse_ports(PORTS)
        ssh = next(s for s in services if s.port == 22)
        self.assertEqual((ssh.name, ssh.state, ssh.proto), ("ssh", "open", "tcp"))

    def test_captures_host(self):
        services = nmap.parse_ports(PORTS)
        self.assertEqual(services[0].host, "45.33.32.156")


class TestNmapServices(unittest.TestCase):
    def test_all_open_ports(self):
        services = nmap.parse_services(SERVICES)
        self.assertEqual(sorted(s.port for s in services), [22, 80, 443])

    def test_captures_version_string(self):
        services = nmap.parse_services(SERVICES)
        ssh = next(s for s in services if s.port == 22)
        self.assertIn("OpenSSH", ssh.version or "")

    def test_marks_critical_port(self):
        services = nmap.parse_services(SERVICES)
        ssh = next(s for s in services if s.port == 22)
        self.assertTrue(ssh.is_critical)


class TestNmapVulns(unittest.TestCase):
    def test_finds_two_vulnerable_scripts(self):
        findings = nmap.parse_vulns(VULNS)
        titles = sorted(f.title for f in findings)
        self.assertEqual(titles, ["smb-vuln-ms17-010", "ssl-poodle"])

    def test_ms17_010_is_critical_via_known_cve(self):
        findings = nmap.parse_vulns(VULNS)
        f = next(f for f in findings if f.title == "smb-vuln-ms17-010")
        self.assertIn("CVE-2017-0143", f.cves)
        self.assertEqual(f.severity, Severity.CRITICAL)
        self.assertEqual(f.source, "nmap-nse")

    def test_poodle_uses_risk_factor_when_cve_unknown_band(self):
        findings = nmap.parse_vulns(VULNS)
        f = next(f for f in findings if f.title == "ssl-poodle")
        self.assertIn("CVE-2014-3566", f.cves)
        self.assertEqual(f.severity, Severity.MEDIUM)

    def test_host_attached(self):
        findings = nmap.parse_vulns(VULNS)
        self.assertTrue(all(f.host == "10.0.0.5" for f in findings))

    def test_clean_scan_has_no_findings(self):
        self.assertEqual(nmap.parse_vulns(CLEAN), [])

    def test_empty_input(self):
        self.assertEqual(nmap.parse_vulns(""), [])
        self.assertEqual(nmap.parse_ports(""), [])


if __name__ == "__main__":
    unittest.main()
