"""MITRE ATT&CK mapping, coverage matrix, and Navigator-layer export.

The scanner performs Reconnaissance (TA0043) and Resource Development (TA0042)
and *indicates* early Initial Access (TA0001) opportunities — it never performs
them. Every finding is tagged; the report renders a coverage matrix and can
export an ATT&CK Navigator layer.
"""
from __future__ import annotations

from typing import Dict, List, Optional

from .models import Finding, Severity

TACTIC_NAMES = {
    "TA0043": "Reconnaissance",
    "TA0042": "Resource Development",
    "TA0001": "Initial Access",
}

# Curated technique metadata (id -> tactic + name). Kept small and offline.
TECHNIQUES: Dict[str, Dict[str, str]] = {
    # Reconnaissance (TA0043)
    "T1595.001": {"tactic": "TA0043", "name": "Active Scanning: Scanning IP Blocks"},
    "T1595.002": {"tactic": "TA0043", "name": "Active Scanning: Vulnerability Scanning"},
    "T1595.003": {"tactic": "TA0043", "name": "Active Scanning: Wordlist Scanning"},
    "T1590.002": {"tactic": "TA0043", "name": "Gather Victim Network Information: DNS"},
    "T1592.002": {"tactic": "TA0043", "name": "Gather Victim Host Information: Software"},
    "T1589.002": {"tactic": "TA0043", "name": "Gather Victim Identity Information: Email Addresses"},
    "T1596.002": {"tactic": "TA0043", "name": "Search Open Technical Databases: WHOIS"},
    "T1596.003": {"tactic": "TA0043", "name": "Search Open Technical Databases: Digital Certificates"},
    "T1596.005": {"tactic": "TA0043", "name": "Search Open Technical Databases: Scan Databases"},
    # Resource Development (TA0042)
    "T1588.005": {"tactic": "TA0042", "name": "Obtain Capabilities: Exploits"},
    "T1588.006": {"tactic": "TA0042", "name": "Obtain Capabilities: Vulnerabilities"},
    "T1588.002": {"tactic": "TA0042", "name": "Obtain Capabilities: Tool"},
    # Initial Access (TA0001) — INDICATED ONLY, never executed
    "T1190": {"tactic": "TA0001", "name": "Exploit Public-Facing Application (indicated)"},
    "T1210": {"tactic": "TA0001", "name": "Exploitation of Remote Services (indicated)"},
    "T1110": {"tactic": "TA0001", "name": "Brute Force (indicated)"},
    "T1133": {"tactic": "TA0001", "name": "External Remote Services (indicated)"},
}

# Default technique id per finding source (the recon act that produced it).
_SOURCE_TECHNIQUE = {
    "nmap-nse": "T1595.002",
    "nuclei": "T1595.002",
    "nikto": "T1595.002",
    "gobuster": "T1595.003",
    "ssl": "T1592.002",
    "smb": "T1595.002",
    "osint": "T1590.002",
    "whois": "T1596.002",
    "crtsh": "T1596.003",
    "shodan": "T1596.005",
}

# Services whose exposure, when a confirmed vuln is present, indicates a
# specific Initial Access technique (brute-forceable / remotely exploitable).
_BRUTE_PORTS = {21, 22, 23, 3389, 5900, 1433, 3306, 5432}


def technique_record(technique_id: str) -> Optional[Dict[str, str]]:
    meta = TECHNIQUES.get(technique_id)
    if not meta:
        return None
    return {"technique": technique_id, "tactic": meta["tactic"], "name": meta["name"]}


def technique_url(technique_id: str) -> str:
    if "." in technique_id:
        base, sub = technique_id.split(".", 1)
        return "https://attack.mitre.org/techniques/%s/%s" % (base, sub)
    return "https://attack.mitre.org/techniques/%s" % technique_id


def technique_for_source(source: Optional[str]) -> Optional[Dict[str, str]]:
    if not source:
        return None
    tid = _SOURCE_TECHNIQUE.get(source)
    return technique_record(tid) if tid else None


def _is_web_source(source: Optional[str]) -> bool:
    return source in ("nuclei", "nikto")


def techniques_for_finding(finding: Finding) -> List[Dict[str, str]]:
    """All ATT&CK techniques a finding maps to: the recon act plus any
    *indicated* Initial Access opportunity for confirmed high/critical issues."""
    out: List[Dict[str, str]] = []

    base = technique_for_source(finding.source)
    if base:
        out.append(base)

    confirmed = finding.severity >= Severity.HIGH or bool(finding.cves)
    if confirmed and finding.severity >= Severity.HIGH:
        if _is_web_source(finding.source):
            indicated = "T1190"
        elif finding.port in _BRUTE_PORTS and not finding.cves:
            indicated = "T1110"
        else:
            indicated = "T1210"
        rec = technique_record(indicated)
        if rec and rec not in out:
            out.append(rec)
    return out


def tag_findings(findings: List[Finding]) -> List[Finding]:
    for finding in findings:
        if finding.mitre:
            continue
        for rec in techniques_for_finding(finding):
            if rec not in finding.mitre:
                finding.mitre.append(rec)
    return findings


def coverage(findings: List[Finding]) -> Dict[str, Dict]:
    """Group tagged techniques by tactic with per-technique counts."""
    result: Dict[str, Dict] = {}
    for finding in findings:
        for tech in finding.mitre:
            tid = tech.get("technique")
            tactic = tech.get("tactic")
            if not tid or not tactic:
                continue
            tactic_entry = result.setdefault(
                tactic, {"name": TACTIC_NAMES.get(tactic, tactic), "techniques": {}}
            )
            tech_entry = tactic_entry["techniques"].setdefault(
                tid, {"name": tech.get("name", tid), "count": 0}
            )
            tech_entry["count"] += 1
    return result


def navigator_layer(findings: List[Finding], name: str = "security-scanner") -> Dict:
    """Build an ATT&CK Navigator layer (v4.5) scoring techniques by hit count."""
    counts: Dict[str, Dict] = {}
    for finding in findings:
        for tech in finding.mitre:
            tid = tech.get("technique")
            if not tid:
                continue
            entry = counts.setdefault(tid, {"score": 0, "name": tech.get("name", tid)})
            entry["score"] += 1
    techniques = [
        {
            "techniqueID": tid,
            "score": data["score"],
            "comment": data["name"],
            "enabled": True,
        }
        for tid, data in sorted(counts.items())
    ]
    return {
        "name": name,
        "versions": {"attack": "14", "navigator": "4.9.1", "layer": "4.5"},
        "domain": "enterprise-attack",
        "description": "Coverage produced by security-scanner (recon + indicated initial access).",
        "techniques": techniques,
        "gradient": {
            "colors": ["#ffe8e8", "#d03b3b"],
            "minValue": 0,
            "maxValue": max([1] + [t["score"] for t in techniques]),
        },
    }
