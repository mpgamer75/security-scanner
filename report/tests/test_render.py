"""Tests for the HTML/JSON/Markdown renderers.

The security-critical behaviors here are (1) every interpolated value is HTML
escaped (the old generator had an injection gap) and (2) the HTML is fully
self-contained/offline (no CDN fonts or external stylesheets).
"""
import json
import re
import unittest

from report import render
from report.models import Assessment, Assets, Finding, Host, Service, Severity


def _sample() -> Assessment:
    assessment = Assessment(
        target="10.0.0.5", url="https://ex.com", domain="ex.com", scan_mode="Standard"
    )
    assessment.hosts = [
        Host(
            ip="10.0.0.5",
            os="Linux 4.x",
            services=[
                Service(port=445, name="microsoft-ds", version="Samba 4.3.11", host="10.0.0.5"),
                Service(port=22, name="ssh", version="OpenSSH 6.6", host="10.0.0.5"),
            ],
        )
    ]
    assessment.findings = [
        Finding(
            title="smb-vuln-ms17-010", severity=Severity.CRITICAL, host="10.0.0.5",
            port=445, cves=["CVE-2017-0143"], source="nmap-nse",
            mitre=[{"technique": "T1595.002", "tactic": "TA0043", "name": "Vuln Scanning"}],
        ),
        Finding(title="apache-detect", severity=Severity.INFO, host="10.0.0.5",
                port=80, source="nuclei"),
    ]
    assessment.assets = Assets(
        subdomains=["www.ex.com", "api.ex.com"], emails=["admin@ex.com"], waf="Cloudflare"
    )
    return assessment


class TestRenderHtmlSecurity(unittest.TestCase):
    def test_escapes_target_injection(self):
        assessment = _sample()
        assessment.target = "<script>alert(1)</script>"
        html = render.render_html(assessment)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)

    def test_escapes_finding_title_injection(self):
        assessment = _sample()
        assessment.findings[0].title = "<img src=x onerror=alert(1)>"
        html = render.render_html(assessment)
        self.assertNotIn("<img src=x onerror=alert(1)>", html)

    def test_no_cdn_fonts_or_external_stylesheets(self):
        html = render.render_html(_sample())
        for banned in ("googleapis", "gstatic", "cdnjs", "jsdelivr", "unpkg"):
            self.assertNotIn(banned, html)
        self.assertNotIn('<link rel="stylesheet"', html)

    def test_is_self_contained_document(self):
        html = render.render_html(_sample())
        self.assertIn("<!doctype html", html.lower())
        self.assertIn("<style", html)
        self.assertIn("<script", html)


class TestRenderHtmlContent(unittest.TestCase):
    def test_shows_risk_score(self):
        html = render.render_html(_sample())
        # one critical -> 65 in the calibrated model
        self.assertIn("65", html)

    def test_shows_findings_and_cve_link(self):
        html = render.render_html(_sample())
        self.assertIn("smb-vuln-ms17-010", html)
        self.assertIn("CVE-2017-0143", html)
        self.assertIn("nvd.nist.gov", html)

    def test_shows_service_and_port(self):
        html = render.render_html(_sample())
        self.assertIn("445", html)
        self.assertIn("Samba 4.3.11", html)

    def test_shows_severity_labels(self):
        html = render.render_html(_sample())
        self.assertIn("critical", html.lower())

    def test_shows_mitre_technique(self):
        html = render.render_html(_sample())
        self.assertIn("T1595.002", html)

    def test_shows_waf_and_subdomains(self):
        html = render.render_html(_sample())
        self.assertIn("Cloudflare", html)
        self.assertIn("www.ex.com", html)

    def test_embedded_json_is_valid(self):
        html = render.render_html(_sample())
        match = re.search(
            r'<script id="report-data" type="application/json">(.*?)</script>',
            html, re.DOTALL,
        )
        self.assertIsNotNone(match)
        data = json.loads(match.group(1).replace("\\u003c", "<"))
        self.assertEqual(len(data["findings"]), 2)

    def test_filter_attribute_matches_chip_value(self):
        # Regression: the row's filter attribute (read by app.js) must use the
        # same value as the severity chip's data-sev-filter, else filtering shows
        # nothing. Rows must carry data-sev="critical", not the numeric level.
        html = render.render_html(_sample())
        self.assertIn('data-sev="critical"', html)
        self.assertIn('data-sev-filter="critical"', html)

    def test_empty_assessment_renders_without_error(self):
        html = render.render_html(Assessment(target="10.0.0.9"))
        self.assertIn("<!doctype html", html.lower())
        self.assertIn("10.0.0.9", html)


class TestRenderMitre(unittest.TestCase):
    def test_coverage_matrix_present(self):
        html = render.render_html(_sample())
        self.assertIn("ATT&amp;CK", html)
        self.assertIn("Reconnaissance", html)  # tactic name in the matrix
        self.assertIn("T1595.002", html)

    def test_navigator_layer_embedded_and_valid(self):
        html = render.render_html(_sample())
        match = re.search(
            r'<script id="navigator-data" type="application/json">(.*?)</script>',
            html, re.DOTALL,
        )
        self.assertIsNotNone(match)
        layer = json.loads(match.group(1).replace("\\u003c", "<"))
        self.assertEqual(layer["domain"], "enterprise-attack")
        self.assertTrue(layer["techniques"])

    def test_render_navigator_is_valid_json(self):
        layer = json.loads(render.render_navigator(_sample()))
        self.assertEqual(layer["domain"], "enterprise-attack")


class TestRenderJson(unittest.TestCase):
    def test_valid_json_with_risk(self):
        data = json.loads(render.render_json(_sample()))
        self.assertEqual(len(data["findings"]), 2)
        self.assertIn("risk_score", data)
        self.assertGreaterEqual(data["risk_score"], 60)

    def test_summary_counts(self):
        data = json.loads(render.render_json(_sample()))
        self.assertEqual(data["summary"]["critical"], 1)
        self.assertEqual(data["summary"]["info"], 1)


class TestRenderMarkdown(unittest.TestCase):
    def test_has_headings_and_target(self):
        md = render.render_markdown(_sample())
        self.assertIn("# ", md)
        self.assertIn("10.0.0.5", md)
        self.assertIn("CVE-2017-0143", md)


class TestRenderInteractiveHooks(unittest.TestCase):
    """The DOM hooks app.js relies on must be present in the rendered HTML."""

    def test_gauge_arc_has_animatable_score(self):
        html = render.render_html(_sample())
        # arc starts at 0 and carries the target score for app.js to animate to.
        self.assertIn('id="gauge-arc"', html)
        self.assertIn('data-score="65"', html)
        self.assertIn('stroke-dasharray="0 100"', html)

    def test_statusline_stats_are_interactive(self):
        html = render.render_html(_sample())
        # severity stats toggle the filter; others jump to a section
        self.assertIn('class="stat" data-sev="critical"', html)
        self.assertIn('data-jump="surface"', html)
        self.assertIn('data-jump="osint"', html)
        self.assertIn('data-jump="attack"', html)

    def test_live_count_and_clear_hooks(self):
        html = render.render_html(_sample())
        self.assertIn('id="findings-count"', html)
        self.assertIn('data-total="2"', html)      # two findings in the sample
        self.assertIn('id="clear-filters"', html)

    def test_sortable_headers_present(self):
        html = render.render_html(_sample())
        self.assertIn('class="sortable" data-sort="severity"', html)
        self.assertIn('data-sort="host"', html)


if __name__ == "__main__":
    unittest.main()
