"""Parse nuclei's default text output lines.

Line shape: ``[template-id] [protocol] [severity] matched-at [extracted]``
e.g. ``[CVE-2021-44228] [http] [critical] https://host:8443/api``
"""
from __future__ import annotations

import re
from typing import List, Optional, Tuple
from urllib.parse import urlparse

from ..models import Finding, Severity
from ..severity import extract_cves

_LINE_RE = re.compile(
    r"^\[(?P<tid>[^\]]+)\]\s+\[(?P<proto>[^\]]+)\]\s+\[(?P<sev>[^\]]+)\]\s+(?P<at>\S+)(?:\s+\[(?P<extra>.*)\])?\s*$"
)

_DEFAULT_PORTS = {"http": 80, "https": 443}


def _host_port(matched_at: str) -> Tuple[Optional[str], Optional[int]]:
    """Extract host + port from a nuclei matched-at (URL or host:port)."""
    target = matched_at
    if "://" not in target:
        target = "//" + target  # let urlparse treat host:port/path uniformly
    parsed = urlparse(target)
    host = parsed.hostname
    port = parsed.port
    if port is None and parsed.scheme in _DEFAULT_PORTS:
        port = _DEFAULT_PORTS[parsed.scheme]
    return host, port


def parse(text: str) -> List[Finding]:
    findings: List[Finding] = []
    for raw in text.splitlines():
        match = _LINE_RE.match(raw.strip())
        if not match:
            continue
        tid = match.group("tid")
        host, port = _host_port(match.group("at"))
        cves = extract_cves(tid + " " + (match.group("extra") or ""))
        findings.append(
            Finding(
                title=tid,
                severity=Severity.from_str(match.group("sev")),
                host=host,
                port=port,
                service=match.group("proto"),
                cves=cves,
                source="nuclei",
                template_id=tid,
                evidence=raw.strip()[:2000],
            )
        )
    return findings
