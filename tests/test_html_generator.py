#!/usr/bin/env python3
"""Unit tests for html_generator.py"""

import sys
import os
import tempfile
import unittest

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import html_generator


class TestXSSEscaping(unittest.TestCase):
    """Test that user-controlled inputs are properly HTML-escaped."""

    def _generate(self, target, url='NONE', domain='NONE', scan_mode='standard'):
        with tempfile.TemporaryDirectory() as tmpdir:
            os.makedirs(f'{tmpdir}/reports', exist_ok=True)
            return html_generator.generate_html_report(tmpdir, target, url, domain, scan_mode)

    def test_target_xss_escaped(self):
        """Script tags in target should be escaped."""
        result = self._generate('<script>alert(1)</script>')
        self.assertNotIn('<script>alert(1)</script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_target_quote_escaped(self):
        """Quotes in target should be escaped."""
        result = self._generate('"onload="alert(1)"')
        self.assertNotIn('"onload="', result)

    def test_url_xss_escaped(self):
        """Script tags in URL should be escaped."""
        result = self._generate('target', url='<script>bad()</script>', domain='NONE')
        self.assertNotIn('<script>bad()</script>', result)

    def test_domain_xss_escaped(self):
        """Script tags in domain should be escaped."""
        result = self._generate('target', url='NONE', domain='<img src=x onerror=alert(1)>')
        self.assertNotIn('<img src=x onerror=alert(1)>', result)

    def test_scan_mode_escaped(self):
        """Malicious scan_mode should be escaped."""
        result = self._generate('target', scan_mode='<b>bold</b>')
        self.assertNotIn('<b>bold</b>', result)
        self.assertIn('&lt;b&gt;', result)

    def test_ampersand_escaped(self):
        """Ampersands in target should be escaped."""
        result = self._generate('target&domain=evil')
        self.assertNotIn('target&domain', result)
        self.assertIn('target&amp;domain', result)


class TestGenerateFindings(unittest.TestCase):
    """Test the _generate_findings helper function."""

    def test_empty_findings_returns_empty_state(self):
        result = html_generator._generate_findings([])
        self.assertIn('empty-state', result)

    def test_findings_are_html_escaped(self):
        findings = ['<script>alert(1)</script>']
        result = html_generator._generate_findings(findings)
        self.assertNotIn('<script>alert(1)</script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_critical_severity_detected(self):
        findings = ['VULNERABLE: ms17-010 EternalBlue detected on port 445']
        result = html_generator._generate_findings(findings)
        self.assertIn('critical', result)

    def test_high_severity_detected(self):
        findings = ['HIGH: dangerous open redirect found']
        result = html_generator._generate_findings(findings)
        self.assertIn('high', result)

    def test_medium_severity_detected(self):
        findings = ['MEDIUM: warning - missing security headers']
        result = html_generator._generate_findings(findings)
        self.assertIn('medium', result)

    def test_copy_button_present(self):
        findings = ['test finding']
        result = html_generator._generate_findings(findings)
        self.assertIn('copy-btn', result)

    def test_long_finding_truncated(self):
        long_finding = 'A' * 600
        result = html_generator._generate_findings([long_finding])
        self.assertIn('...', result)

    def test_custom_empty_message(self):
        result = html_generator._generate_findings([], empty_message='Custom message here')
        self.assertIn('Custom message here', result)


class TestGenerateServicesTable(unittest.TestCase):
    """Test the _generate_services_table helper function."""

    def test_empty_services_returns_empty_state(self):
        result = html_generator._generate_services_table([], [])
        self.assertIn('empty-state', result)

    def test_services_are_html_escaped(self):
        services = ['<script>evil()</script> 80/tcp open']
        result = html_generator._generate_services_table(services, [])
        self.assertNotIn('<script>evil()</script>', result)
        self.assertIn('&lt;script&gt;', result)

    def test_critical_port_gets_badge(self):
        services = ['445/tcp open microsoft-ds']
        result = html_generator._generate_services_table(services, services)
        self.assertIn('CRITICAL', result)

    def test_non_critical_port_no_badge(self):
        services = ['8080/tcp open http-proxy']
        result = html_generator._generate_services_table(services, [])
        self.assertNotIn('service-badge critical', result)


class TestDonutChart(unittest.TestCase):
    """Test the _generate_donut_chart helper function."""

    def test_empty_stats_returns_empty(self):
        stats = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        result = html_generator._generate_donut_chart(stats)
        self.assertEqual(result, '')

    def test_chart_contains_svg(self):
        stats = {'critical': 3, 'high': 5, 'medium': 10, 'low': 2}
        result = html_generator._generate_donut_chart(stats)
        self.assertIn('<svg', result)
        self.assertIn('donut-legend', result)

    def test_chart_shows_totals(self):
        stats = {'critical': 3, 'high': 5, 'medium': 10, 'low': 2}
        result = html_generator._generate_donut_chart(stats)
        self.assertIn('20', result)  # total = 3+5+10+2 = 20


class TestHTMLStructure(unittest.TestCase):
    """Test overall HTML structure of generated report."""

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        os.makedirs(f'{self.tmpdir}/reports', exist_ok=True)
        self.report = html_generator.generate_html_report(
            self.tmpdir, 'test.example.com',
            'http://test.example.com', 'test.example.com', 'standard'
        )

    def test_has_doctype(self):
        self.assertTrue(self.report.startswith('<!DOCTYPE html>'))

    def test_has_lang_attribute(self):
        self.assertIn('lang="en"', self.report)

    def test_has_charset_meta(self):
        self.assertIn('charset="UTF-8"', self.report)

    def test_has_viewport_meta(self):
        self.assertIn('viewport', self.report)

    def test_has_main_landmark(self):
        self.assertIn('<main', self.report)

    def test_has_skip_nav(self):
        self.assertIn('skip-nav', self.report)

    def test_has_aria_roles(self):
        self.assertIn('role="tablist"', self.report)
        self.assertIn('role="tab"', self.report)
        self.assertIn('role="tabpanel"', self.report)

    def test_has_theme_toggle(self):
        self.assertIn('themeToggle', self.report)

    def test_has_search_input(self):
        self.assertIn('searchInput', self.report)

    def test_has_scroll_progress(self):
        self.assertIn('scroll-progress', self.report)

    def test_version_in_footer(self):
        self.assertIn(html_generator.VERSION, self.report)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)


if __name__ == '__main__':
    unittest.main(verbosity=2)
