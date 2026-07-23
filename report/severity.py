"""Severity classification, CVE extraction, risk scoring, and finding dedup.

This module is the corrective replacement for the old approach of counting the
literal strings ``vulnerable`` / ``critical`` / ``osvdb`` in raw tool output.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .models import Finding, Severity

_CVE_RE = re.compile(r"CVE-\d{4}-\d{4,7}", re.IGNORECASE)

# A small, curated table of famous CVEs whose severity we can assert without a
# network CVSS lookup (the report must work fully offline / air-gapped).
_KNOWN_CVE_SEVERITY = {
    "CVE-2017-0143": Severity.CRITICAL,  # EternalBlue family (MS17-010)
    "CVE-2017-0144": Severity.CRITICAL,
    "CVE-2017-0145": Severity.CRITICAL,
    "CVE-2017-0146": Severity.CRITICAL,
    "CVE-2017-0147": Severity.HIGH,
    "CVE-2017-0148": Severity.CRITICAL,
    "CVE-2008-4250": Severity.CRITICAL,  # MS08-067
    "CVE-2019-0708": Severity.CRITICAL,  # BlueKeep
    "CVE-2021-44228": Severity.CRITICAL,  # Log4Shell
    "CVE-2021-45046": Severity.CRITICAL,  # Log4Shell follow-up
    "CVE-2014-0160": Severity.HIGH,       # Heartbleed
    "CVE-2014-6271": Severity.CRITICAL,   # Shellshock
    "CVE-2014-3566": Severity.MEDIUM,     # POODLE
    "CVE-2016-5195": Severity.HIGH,       # Dirty COW
    "CVE-2021-26855": Severity.CRITICAL,  # ProxyLogon
    "CVE-2019-19781": Severity.CRITICAL,  # Citrix
    "CVE-2020-1472": Severity.CRITICAL,   # Zerologon
}


def extract_cves(text: Optional[str]) -> List[str]:
    """Return uppercased, de-duplicated CVE ids in first-seen order."""
    if not text:
        return []
    seen: List[str] = []
    for match in _CVE_RE.findall(text):
        cve = match.upper()
        if cve not in seen:
            seen.append(cve)
    return seen


def severity_from_cvss(score: Optional[float]) -> Severity:
    """Map a CVSS v3 base score to a severity band (CVSS v3 qualitative ranges)."""
    if score is None:
        return Severity.INFO
    try:
        value = float(score)
    except (TypeError, ValueError):
        return Severity.INFO
    if value >= 9.0:
        return Severity.CRITICAL
    if value >= 7.0:
        return Severity.HIGH
    if value >= 4.0:
        return Severity.MEDIUM
    if value > 0.0:
        return Severity.LOW
    return Severity.INFO


def severity_for_cve(cve: Optional[str]) -> Optional[Severity]:
    """Known severity for a famous CVE, or None if we don't have it curated."""
    if not cve:
        return None
    return _KNOWN_CVE_SEVERITY.get(cve.upper())


# Risk model: dominated by the single worst finding (base), plus a bounded
# contribution from the volume of remaining findings. Calibrated so a single
# critical already reads as high risk, while noise (many info items) does not.
_BASE = {
    Severity.CRITICAL: 65,
    Severity.HIGH: 45,
    Severity.MEDIUM: 25,
    Severity.LOW: 8,
    Severity.INFO: 2,
}
_VOLUME = {
    Severity.CRITICAL: 6.0,
    Severity.HIGH: 3.0,
    Severity.MEDIUM: 1.5,
    Severity.LOW: 0.5,
    Severity.INFO: 0.0,
}


def risk_score(findings: List[Finding]) -> int:
    """Compute a calibrated 0-100 risk score from a list of findings."""
    if not findings:
        return 0
    max_sev = max(f.severity for f in findings)
    counts: dict = {}
    for finding in findings:
        counts[finding.severity] = counts.get(finding.severity, 0) + 1
    volume = 0.0
    for sev, count in counts.items():
        # one instance of the worst severity is already captured by the base
        extra = count - 1 if sev == max_sev else count
        volume += _VOLUME[sev] * extra
    return int(min(100, round(_BASE[max_sev] + volume)))


def _dedupe_key(finding: Finding):
    if finding.cves:
        return (finding.host, finding.port, tuple(sorted(c.upper() for c in finding.cves)))
    return (finding.host, finding.port, (finding.title or "").strip().lower())


def _merge_into(primary: Finding, secondary: Finding) -> Finding:
    for cve in secondary.cves:
        if cve not in primary.cves:
            primary.cves.append(cve)
    for ref in secondary.references:
        if ref not in primary.references:
            primary.references.append(ref)
    for tech in secondary.mitre:
        if tech not in primary.mitre:
            primary.mitre.append(tech)
    return primary


def dedupe(findings: List[Finding]) -> List[Finding]:
    """Collapse findings that describe the same issue on the same host:port.

    Two findings merge when they share host+port and either the same CVE set or
    (absent CVEs) the same title. The higher-severity finding is kept as primary;
    CVEs / references / MITRE tags are unioned in.
    """
    by_key: dict = {}
    order: list = []
    for finding in findings:
        key = _dedupe_key(finding)
        if key not in by_key:
            by_key[key] = finding
            order.append(key)
            continue
        existing = by_key[key]
        if finding.severity > existing.severity:
            by_key[key] = _merge_into(finding, existing)
        else:
            by_key[key] = _merge_into(existing, finding)
    return [by_key[key] for key in order]
