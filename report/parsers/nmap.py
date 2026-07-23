"""Parse nmap human-readable output into Services and Findings.

Handles the three output styles the scanner produces: a plain port table
(``-sS``), a service/version table (``-sV -sC``), and NSE ``vuln`` script
blocks (``| script-id:`` ... ``VULNERABLE`` ... ``CVE:...``).
"""
from __future__ import annotations

import re
from typing import List, Optional

from ..models import Finding, Service, Severity
from ..severity import extract_cves, severity_for_cve

_HOST_RE = re.compile(r"Nmap scan report for (\S+?)(?:\s+\(([0-9.]+)\))?\s*$")
# e.g. "22/tcp    open  ssh           OpenSSH 6.6.1p1 ..."
_PORT_RE = re.compile(r"^(\d{1,5})/(tcp|udp)\s+(\S+)\s+(\S+)(?:\s+(.*\S))?\s*$")
# NSE script header: a single leading pipe, one space, an id containing a dash.
_SCRIPT_HEADER_RE = re.compile(r"^\|_?\s([a-zA-Z0-9][\w.\-]*):")
_RISK_RE = re.compile(r"Risk factor:\s*(\w+)", re.IGNORECASE)


def _host_from_line(line: str) -> Optional[str]:
    match = _HOST_RE.match(line.strip())
    if not match:
        return None
    # prefer the parenthesised IP, else the reported name
    return match.group(2) or match.group(1)


def _parse_port_table(text: str, want_version: bool) -> List[Service]:
    services: List[Service] = []
    host: Optional[str] = None
    for raw in text.splitlines():
        line = raw.rstrip()
        maybe_host = _host_from_line(line)
        if maybe_host:
            host = maybe_host
            continue
        match = _PORT_RE.match(line.strip())
        if not match:
            continue
        port, proto, state, name, rest = match.groups()
        if state != "open":
            continue
        service = Service(
            port=int(port), proto=proto, state="open", name=name, host=host
        )
        if want_version and rest:
            service.version = rest.strip()
        services.append(service)
    return services


def parse_ports(text: str) -> List[Service]:
    """Parse a plain nmap port table; returns open services only."""
    return _parse_port_table(text, want_version=False)


def parse_services(text: str) -> List[Service]:
    """Parse an nmap ``-sV`` service table including the version column."""
    return _parse_port_table(text, want_version=True)


def _finding_from_block(script_id: str, block: str, host: Optional[str]) -> Finding:
    cves = extract_cves(block)
    known = [s for s in (severity_for_cve(c) for c in cves) if s is not None]
    if known:
        sev = max(known)
    else:
        risk = _RISK_RE.search(block)
        sev = Severity.from_str(risk.group(1)) if risk else Severity.HIGH
    return Finding(
        title=script_id,
        severity=sev,
        host=host,
        cves=cves,
        source="nmap-nse",
        template_id=script_id,
        evidence=block.strip()[:2000],
    )


def parse_vulns(text: str) -> List[Finding]:
    """Extract findings from nmap NSE ``vuln`` script output blocks."""
    host: Optional[str] = None
    findings: List[Finding] = []
    cur_id: Optional[str] = None
    cur: List[str] = []

    def flush() -> None:
        nonlocal cur_id, cur
        if cur_id and cur:
            block = "\n".join(cur)
            if "VULNERABLE" in block.upper() or extract_cves(block):
                findings.append(_finding_from_block(cur_id, block, host))
        cur_id, cur = None, []

    for raw in text.splitlines():
        maybe_host = _host_from_line(raw)
        if maybe_host:
            host = maybe_host
            continue
        header = _SCRIPT_HEADER_RE.match(raw)
        if header:
            flush()
            cur_id = header.group(1)
            cur = [raw]
        elif cur_id is not None and raw.startswith("|"):
            cur.append(raw)
        else:
            flush()
    flush()
    return findings
