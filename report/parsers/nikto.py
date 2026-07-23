"""Parse nikto's ``+``-prefixed output lines into findings.

Nikto does not emit machine severities, so severity is a keyword heuristic.
Pure banner/summary lines (Target, Server, timing, request counts) are skipped.
"""
from __future__ import annotations

import re
from typing import List

from ..models import Finding, Severity
from ..severity import extract_cves

# Leading text (after "+ ") that identifies a banner/summary line, not a finding.
_SKIP_PREFIXES = (
    "target ip",
    "target hostname",
    "target port",
    "start time",
    "end time",
    "server:",
    "retrieved",
    "ssl info",
    "root page",
    "allowed http",
    "no cgi",
    "scan terminated",
    "host(s) tested",
    "ssl certificate",
)
_SUMMARY_RE = re.compile(r"\d+\s+requests?:", re.IGNORECASE)

# Keyword -> minimum severity, checked most-severe first.
_SEVERITY_KEYWORDS = [
    (Severity.CRITICAL, ("remote code", " rce", "command injection", "os-shell")),
    (Severity.HIGH, ("sql injection", "sqli", "shell", "traversal", "lfi", "rfi",
                      "default cred", "default account", "authentication bypass")),
    (Severity.MEDIUM, ("xss", "cross site", "backup", "osvdb", "cve-",
                       "outdated", "injection", "disclosure")),
    (Severity.LOW, ("directory indexing", "default file", "index of",
                    "config", "readme", "phpinfo", "header")),
]


def _severity_for(line: str) -> Severity:
    lower = line.lower()
    for sev, keywords in _SEVERITY_KEYWORDS:
        if any(k in lower for k in keywords):
            return sev
    return Severity.INFO


def parse(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line.startswith("+ "):
            continue
        body = line[2:].strip()
        low = body.lower()
        if low.startswith(_SKIP_PREFIXES) or _SUMMARY_RE.search(body):
            continue
        findings.append(
            Finding(
                title=body[:300],
                severity=_severity_for(body),
                cves=extract_cves(body),
                source="nikto",
                evidence=body[:2000],
            )
        )
    return findings
