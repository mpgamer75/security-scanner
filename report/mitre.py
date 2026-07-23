"""Lightweight MITRE ATT&CK tagging for findings.

This is the report-milestone seed of the mapping; Phase 3 expands it into a
full technique table + ATT&CK Navigator layer export. Every finding gets at
least one technique so the report can render a MITRE column and coverage strip.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import Finding

# Curated ATT&CK technique metadata used across the tool.
TECHNIQUES: Dict[str, Dict[str, str]] = {
    "T1595.002": {"tactic": "TA0043", "name": "Active Scanning: Vulnerability Scanning"},
    "T1595.003": {"tactic": "TA0043", "name": "Active Scanning: Wordlist Scanning"},
    "T1590.002": {"tactic": "TA0043", "name": "Gather Victim Network Information: DNS"},
    "T1592.002": {"tactic": "TA0043", "name": "Gather Victim Host Information: Software"},
    "T1589.002": {"tactic": "TA0043", "name": "Gather Victim Identity Information: Email"},
    "T1596.003": {"tactic": "TA0043", "name": "Search Open Technical Databases: Digital Certificates"},
    "T1588.006": {"tactic": "TA0042", "name": "Obtain Capabilities: Vulnerabilities"},
    "T1190": {"tactic": "TA0001", "name": "Exploit Public-Facing Application (indicated)"},
}

# Default technique id per finding source.
_SOURCE_TECHNIQUE: Dict[str, str] = {
    "nmap-nse": "T1595.002",
    "nuclei": "T1595.002",
    "nikto": "T1595.002",
    "gobuster": "T1595.003",
    "ssl": "T1592.002",
    "smb": "T1595.002",
    "osint": "T1590.002",
}


def _technique_record(technique_id: str) -> Optional[Dict[str, str]]:
    meta = TECHNIQUES.get(technique_id)
    if not meta:
        return None
    return {"technique": technique_id, "tactic": meta["tactic"], "name": meta["name"]}


def technique_for_source(source: Optional[str]) -> Optional[Dict[str, str]]:
    if not source:
        return None
    tid = _SOURCE_TECHNIQUE.get(source)
    return _technique_record(tid) if tid else None


def tag_findings(findings: List[Finding]) -> List[Finding]:
    for finding in findings:
        if finding.mitre:
            continue
        record = technique_for_source(finding.source)
        if record:
            finding.mitre.append(record)
        # A confirmed vuln with a CVE is an indicated exploitation opportunity.
        if finding.cves and finding.severity.name in ("CRITICAL", "HIGH"):
            indicated = _technique_record("T1190")
            if indicated and indicated not in finding.mitre:
                finding.mitre.append(indicated)
    return findings
