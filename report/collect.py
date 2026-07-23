"""Assemble a normalized Assessment from a redteam_*/ output directory.

This is the integration point the HTML generator calls. It reads whatever raw
tool outputs are present (missing files are fine) and produces one deduped,
MITRE-tagged findings model.
"""
from __future__ import annotations

import os
from typing import List

from . import mitre, severity
from .models import Assessment, Assets, Finding, Host, Service
from .parsers import nikto, nmap, nuclei, osint


def _read(*parts: str) -> str:
    path = os.path.join(*parts)
    try:
        with open(path, "r", encoding="utf-8", errors="ignore") as handle:
            return handle.read()
    except (FileNotFoundError, NotADirectoryError, IsADirectoryError, OSError):
        return ""


def _group_hosts(services: List[Service], fallback_host: str) -> List[Host]:
    merged = {}
    order = []
    for svc in services:
        host = svc.host or fallback_host or "target"
        key = (host, svc.port, svc.proto)
        if key not in merged:
            merged[key] = Service(
                port=svc.port, proto=svc.proto, state=svc.state,
                name=svc.name, product=svc.product, version=svc.version, host=host,
            )
            order.append(key)
        else:
            existing = merged[key]
            existing.version = existing.version or svc.version
            existing.name = existing.name or svc.name
            existing.product = existing.product or svc.product

    hosts = {}
    host_order = []
    for key in order:
        svc = merged[key]
        host = svc.host
        if host not in hosts:
            hosts[host] = Host(ip=host, services=[])
            host_order.append(host)
        hosts[host].services.append(svc)
    for host in hosts.values():
        host.services.sort(key=lambda s: (s.proto, s.port))
    return [hosts[h] for h in host_order]


def build_assessment(
    outdir: str,
    target: str = "",
    url: str = "",
    domain: str = "",
    scan_mode: str = "Standard",
) -> Assessment:
    assessment = Assessment(
        target=target,
        url=url or None,
        domain=domain or None,
        scan_mode=scan_mode,
    )

    services: List[Service] = []
    services += nmap.parse_ports(_read(outdir, "network", "nmap_ports.txt"))
    services += nmap.parse_services(_read(outdir, "network", "nmap_services.txt"))
    assessment.hosts = _group_hosts(services, fallback_host=target)

    findings: List[Finding] = []
    findings += nmap.parse_vulns(_read(outdir, "network", "nmap_vulns.txt"))
    findings += nmap.parse_vulns(_read(outdir, "network", "nmap_critical_vulns.txt"))
    findings += nmap.parse_vulns(_read(outdir, "network", "smb_enum.txt"))
    findings += nmap.parse_vulns(_read(outdir, "web", "ssl_analysis.txt"))
    findings += nuclei.parse(_read(outdir, "web", "nuclei.txt"))
    findings += nikto.parse(_read(outdir, "web", "nikto.txt"))

    findings = severity.dedupe(findings)
    mitre.tag_findings(findings)
    # Most severe first, stable within a severity.
    findings.sort(key=lambda f: f.severity, reverse=True)
    assessment.findings = findings

    assessment.assets = Assets(
        subdomains=osint.parse_subdomains(_read(outdir, "osint", "all_subdomains.txt")),
        emails=osint.parse_emails(_read(outdir, "osint", "emails.txt")),
        urls=[],
        waf=osint.parse_waf(_read(outdir, "web", "wafw00f.txt")),
    )
    return assessment
