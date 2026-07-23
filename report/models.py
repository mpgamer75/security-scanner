"""Core data model for assessment findings.

A single normalized `Finding` type replaces the fragile substring counting that
previously lived in both `security` (bash) and `html_generator.py`.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional


class Severity(IntEnum):
    """Ordered severity levels. Higher int == more severe (so `>` comparisons work)."""

    INFO = 0
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

    @property
    def label(self) -> str:
        return self.name.lower()

    @classmethod
    def from_str(cls, value: Any) -> "Severity":
        """Map a tool's severity string to a level. Unknown/empty -> INFO.

        Accepts plain (``high``) and bracketed nuclei tags (``[high]``).
        """
        if not value:
            return cls.INFO
        v = str(value).strip().lower().strip("[]").strip()
        return _SEVERITY_ALIASES.get(v, cls.INFO)


_SEVERITY_ALIASES: Dict[str, Severity] = {
    "critical": Severity.CRITICAL,
    "crit": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "moderate": Severity.MEDIUM,
    "low": Severity.LOW,
    "info": Severity.INFO,
    "informational": Severity.INFO,
    "information": Severity.INFO,
    "none": Severity.INFO,
    "unknown": Severity.INFO,
}


@dataclass
class Finding:
    """One normalized security finding."""

    title: str
    severity: Severity = Severity.INFO
    host: Optional[str] = None
    port: Optional[int] = None
    proto: str = "tcp"
    service: Optional[str] = None
    cvss: Optional[float] = None
    cves: List[str] = field(default_factory=list)
    references: List[str] = field(default_factory=list)
    source: Optional[str] = None
    template_id: Optional[str] = None
    evidence: Optional[str] = None
    mitre: List[Dict[str, str]] = field(default_factory=list)
    owasp: Optional[str] = None
    remediation: Optional[str] = None
    id: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "severity": self.severity.label,
            "host": self.host,
            "port": self.port,
            "proto": self.proto,
            "service": self.service,
            "cvss": self.cvss,
            "cves": list(self.cves),
            "references": list(self.references),
            "source": self.source,
            "template_id": self.template_id,
            "evidence": self.evidence,
            "mitre": list(self.mitre),
            "owasp": self.owasp,
            "remediation": self.remediation,
        }


@dataclass
class Service:
    """An open port / service on a host."""

    port: int
    proto: str = "tcp"
    state: str = "open"
    name: Optional[str] = None
    product: Optional[str] = None
    version: Optional[str] = None
    host: Optional[str] = None

    CRITICAL_PORTS = {21, 22, 23, 25, 135, 139, 445, 1433, 3306, 3389, 5432, 5900, 6379}

    @property
    def is_critical(self) -> bool:
        return self.port in self.CRITICAL_PORTS

    def to_dict(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "proto": self.proto,
            "state": self.state,
            "name": self.name,
            "product": self.product,
            "version": self.version,
            "host": self.host,
            "critical": self.is_critical,
        }


@dataclass
class Host:
    ip: Optional[str] = None
    hostname: Optional[str] = None
    os: Optional[str] = None
    services: List[Service] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "ip": self.ip,
            "hostname": self.hostname,
            "os": self.os,
            "services": [s.to_dict() for s in self.services],
        }


@dataclass
class Assets:
    """Passive/OSINT-discovered assets."""

    subdomains: List[str] = field(default_factory=list)
    emails: List[str] = field(default_factory=list)
    urls: List[str] = field(default_factory=list)
    waf: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "subdomains": list(self.subdomains),
            "emails": list(self.emails),
            "urls": list(self.urls),
            "waf": self.waf,
        }


@dataclass
class Assessment:
    """The full normalized result of one scan run."""

    target: str = ""
    url: Optional[str] = None
    domain: Optional[str] = None
    scan_mode: str = "Standard"
    version: str = "2.4.0"
    hosts: List[Host] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    assets: Assets = field(default_factory=Assets)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "url": self.url,
            "domain": self.domain,
            "scan_mode": self.scan_mode,
            "version": self.version,
            "hosts": [h.to_dict() for h in self.hosts],
            "findings": [f.to_dict() for f in self.findings],
            "assets": self.assets.to_dict(),
        }
