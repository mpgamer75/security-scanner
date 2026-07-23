"""Render an Assessment to a self-contained offline HTML report (+ JSON + Markdown).

Design goals: everything HTML-escaped (no injection), no external resources
(CDN fonts / stylesheets), severity always carried by a labelled chip.
"""
from __future__ import annotations

import html
import json
import os
from datetime import datetime
from typing import Dict, List

from . import mitre
from . import severity as sev
from .models import Assessment, Finding, Severity

_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# (letter, label) per severity — the mandatory secondary encoding.
_SEV_META = {
    Severity.CRITICAL: ("C", "critical"),
    Severity.HIGH: ("H", "high"),
    Severity.MEDIUM: ("M", "medium"),
    Severity.LOW: ("L", "low"),
    Severity.INFO: ("I", "info"),
}
_SEV_ORDER = [Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW, Severity.INFO]
_ACCENT_CLASS = {
    Severity.CRITICAL: "crit-accent",
    Severity.HIGH: "high-accent",
    Severity.MEDIUM: "med-accent",
    Severity.LOW: "low-accent",
    Severity.INFO: "info-accent",
}

_TACTIC_NAMES = {
    "TA0043": "Reconnaissance",
    "TA0042": "Resource Development",
    "TA0001": "Initial Access",
}

# Minimal per-issue exploitation guidance seed (expanded in Phase 3).
_GUIDANCE = {
    "CVE-2017-0143": ("EternalBlue / MS17-010 — SMBv1 RCE.",
                      "Patch MS17-010 and disable SMBv1. Public exploits exist "
                      "(Exploit-DB, msf exploit/windows/smb/ms17_010_eternalblue)."),
    "CVE-2021-44228": ("Log4Shell — Log4j JNDI RCE.",
                       "Upgrade Log4j >= 2.17. Confirm with an out-of-band callback "
                       "before asserting exploitability."),
    "CVE-2019-0708": ("BlueKeep — RDP pre-auth RCE.",
                      "Patch and enable NLA. Treat as critical exposure on 3389/tcp."),
    "CVE-2014-0160": ("Heartbleed — TLS memory disclosure.",
                      "Update OpenSSL, rotate keys/certs, and force credential resets."),
}


def _esc(value) -> str:
    return html.escape("" if value is None else str(value))


def _mitre_url(technique_id: str) -> str:
    if "." in technique_id:
        base, sub = technique_id.split(".", 1)
        return "https://attack.mitre.org/techniques/%s/%s" % (base, sub)
    return "https://attack.mitre.org/techniques/%s" % technique_id


def _load_asset(name: str) -> str:
    with open(os.path.join(_TEMPLATE_DIR, name), "r", encoding="utf-8") as handle:
        return handle.read()


def _severity_counts(findings: List[Finding]) -> Dict[str, int]:
    counts = {meta[1]: 0 for meta in _SEV_META.values()}
    for finding in findings:
        counts[finding.severity.label] += 1
    return counts


def _risk_level(score: int) -> str:
    if score >= 70:
        return "critical"
    if score >= 40:
        return "high"
    if score >= 20:
        return "medium"
    return "low"


# --------------------------------------------------------------------------- #
# HTML fragments
# --------------------------------------------------------------------------- #
def _sev_chip(severity: Severity) -> str:
    letter, label = _SEV_META[severity]
    return (
        '<span class="sev sev-%s"><span class="glyph" aria-hidden="true">%s</span>%s</span>'
        % (label, letter, label.upper())
    )


def _gauge(score: int, level: str) -> str:
    return (
        '<div class="gauge">'
        '<svg viewBox="0 0 120 72" width="120" height="72" role="img" '
        'aria-label="Risk score %d of 100">'
        '<path d="M8 60 A 52 52 0 0 1 112 60" fill="none" stroke="var(--hair-strong)" '
        'stroke-width="10" stroke-linecap="round"/>'
        '<path d="M8 60 A 52 52 0 0 1 112 60" fill="none" stroke="var(--sev-%s)" '
        'stroke-width="10" stroke-linecap="round" pathLength="100" '
        'stroke-dasharray="%d 100"/></svg>'
        '<div class="gauge-score num">%d<span style="font-size:1rem;color:var(--ink-3)">/100</span></div>'
        '<div class="gauge-level" style="color:var(--sev-%s)">%s risk</div>'
        "</div>" % (score, level, score, score, level, level.upper())
    )


def _spine(counts: Dict[str, int], total: int) -> str:
    rows = []
    for severity in _SEV_ORDER:
        label = severity.label
        count = counts[label]
        # min flex so empty tiers stay visible/clickable but tiny
        grow = max(count, 0.18)
        if count == 0:
            rows.append(
                '<div class="spine-seg empty seg-%s" data-sev-filter="%s" style="flex:%s">'
                '<span class="lbl">%s</span><span>0</span></div>'
                % (label, label, grow, label.upper())
            )
        else:
            rows.append(
                '<button class="spine-seg seg-%s" data-sev-filter="%s" aria-pressed="false" '
                'style="flex:%s" title="Filter to %s findings">'
                '<span class="lbl">%s</span><span class="num">%d</span></button>'
                % (label, label, grow, label, label.upper(), count)
            )
    return (
        '<aside class="spine"><div class="spine-title">Severity</div>'
        '<div class="spine-bar" role="group" aria-label="Findings by severity">%s</div>'
        '<div class="spine-hint">%d findings. Click a band to filter.</div></aside>'
        % ("".join(rows), total)
    )


def _attack_strip(findings: List[Finding]) -> str:
    tally: Dict[str, Dict] = {}
    for finding in findings:
        for tech in finding.mitre:
            tid = tech.get("technique", "")
            if not tid:
                continue
            entry = tally.setdefault(
                tid,
                {"name": tech.get("name", tid), "tactic": tech.get("tactic", ""), "count": 0},
            )
            entry["count"] += 1
    if not tally:
        return ""
    cells = []
    for tid in sorted(tally):
        entry = tally[tid]
        indicated = " indicated" if entry["tactic"] == "TA0001" else ""
        cells.append(
            '<a class="tactic%s" href="%s" target="_blank" rel="noopener">'
            '<span class="id mono">%s</span><span class="n">%s</span>'
            '<span class="c num">%d</span></a>'
            % (indicated, _mitre_url(tid), _esc(tid), _esc(entry["name"]), entry["count"])
        )
    return '<nav class="attack wrap" aria-label="ATT&amp;CK coverage">%s</nav>' % "".join(cells)


def _cve_links(cves: List[str]) -> str:
    if not cves:
        return '<span class="f-src">&mdash;</span>'
    parts = []
    for cve in cves:
        cve_e = _esc(cve)
        parts.append(
            '<span><a href="https://nvd.nist.gov/vuln/detail/%s" target="_blank" '
            'rel="noopener">%s</a> '
            '<a href="https://www.exploit-db.com/search?cve=%s" target="_blank" '
            'rel="noopener" title="Exploit-DB">[edb]</a></span>'
            % (cve_e, cve_e, cve_e)
        )
    return '<div class="cve-list">%s</div>' % "".join(parts)


def _tech_cell(finding: Finding) -> str:
    if not finding.mitre:
        return "&mdash;"
    links = []
    for tech in finding.mitre:
        tid = tech.get("technique", "")
        if tid:
            links.append(
                '<a href="%s" target="_blank" rel="noopener" title="%s">%s</a>'
                % (_mitre_url(tid), _esc(tech.get("name", "")), _esc(tid))
            )
    return " ".join(links)


def _findings_table(findings: List[Finding]) -> str:
    if not findings:
        return (
            '<div class="empty-hint">No findings parsed. Either the target is clean '
            "or the relevant scans were not run.</div>"
        )
    body = []
    for i, f in enumerate(findings):
        loc = _esc(f.host or "")
        if f.port:
            loc += ":" + str(f.port)
        search_hay = " ".join(
            filter(None, [f.title, f.host, str(f.port or ""), f.source, " ".join(f.cves),
                          " ".join(t.get("technique", "") for t in f.mitre)])
        )
        ev_id = "ev-%d" % i
        has_ev = bool(f.evidence)
        expand = (
            '<button class="expand-btn" data-target="%s" aria-expanded="false" '
            'aria-label="Toggle evidence">+</button>' % ev_id
            if has_ev else ""
        )
        body.append(
            '<tr class="frow %s" data-severity="%d" data-sev="%s" data-host="%s" data-port="%s" '
            'data-title="%s" data-search="%s">'
            "<td>%s</td>"
            '<td class="f-loc">%s</td>'
            '<td class="f-title">%s %s</td>'
            "<td>%s</td>"
            '<td class="f-tech">%s</td>'
            '<td class="f-src">%s</td>'
            "</tr>"
            % (
                _ACCENT_CLASS[f.severity], int(f.severity), f.severity.label, _esc(f.host or ""),
                _esc(f.port or 0), _esc(f.title.lower()), _esc(search_hay.lower()),
                _sev_chip(f.severity), loc or "&mdash;", _esc(f.title), expand,
                _cve_links(f.cves), _tech_cell(f), _esc(f.source or ""),
            )
        )
        if has_ev:
            body.append(
                '<tr class="evidence-row hidden" id="%s"><td colspan="6">'
                '<div class="evidence">%s</div></td></tr>'
                % (ev_id, _esc(f.evidence))
            )
    filters = "".join(
        '<button class="chip" data-sev-filter="%s" aria-pressed="false">'
        '<span class="dot" style="background:var(--sev-%s)"></span>%s</button>'
        % (s.label, s.label, s.label) for s in _SEV_ORDER
    )
    return (
        '<div class="toolbar">'
        '<input id="finding-search" class="search" type="search" '
        'placeholder="search findings, hosts, CVEs, ATT&amp;CK ids…" aria-label="Search findings">'
        '<div class="filters">%s</div>'
        '<button class="btn" id="export-json">Export JSON</button>'
        '<button class="btn" id="copy-markdown">Copy Markdown</button>'
        "</div>"
        '<table class="tbl" id="findings-table"><thead><tr>'
        '<th class="sortable" data-sort="severity">Severity</th>'
        '<th class="sortable" data-sort="host">Host:Port</th>'
        '<th class="sortable" data-sort="title">Finding</th>'
        "<th>CVE</th><th>ATT&amp;CK</th>"
        '<th class="sortable" data-sort="source">Source</th>'
        "</tr></thead><tbody>%s</tbody></table>"
        '<div class="empty-hint hidden" id="findings-empty">No findings match the current filter.</div>'
        % (filters, "".join(body))
    )


def _surface(assessment: Assessment) -> str:
    if not assessment.hosts or not any(h.services for h in assessment.hosts):
        return '<div class="empty-hint">No open services recorded.</div>'
    blocks = []
    for host in assessment.hosts:
        if not host.services:
            continue
        rows = []
        for svc in host.services:
            crit = " crit" if svc.is_critical else ""
            tag = '<span class="tag">critical port</span>' if svc.is_critical else ""
            rows.append(
                '<tr class="%s"><td>%s/%s</td><td>%s</td><td>%s</td><td>%s</td></tr>'
                % (crit.strip(), _esc(svc.port), _esc(svc.proto), _esc(svc.name or "—"),
                   _esc(svc.version or "—"), tag)
            )
        os_line = '<span class="os">%s</span>' % _esc(host.os) if host.os else ""
        blocks.append(
            '<div class="host-block"><div class="host-head"><span>%s</span>%s'
            '<span class="os">%d services</span></div>'
            '<table class="svc-tbl"><thead><tr><th>Port</th><th>Proto</th>'
            "<th>Service</th><th>Version</th><th></th></tr></thead><tbody>%s</tbody></table></div>"
            % (_esc(host.ip or assessment.target), os_line, len(host.services), "".join(rows))
        )
    return "".join(blocks)


def _mitre_matrix(findings: List[Finding]) -> str:
    cov = mitre.coverage(findings)
    if not cov:
        return '<div class="empty-hint">No ATT&amp;CK techniques recorded.</div>'
    order = ["TA0043", "TA0042", "TA0001"]
    tactics = [t for t in order if t in cov] + [t for t in cov if t not in order]
    cols = []
    for tactic in tactics:
        entry = cov[tactic]
        cells = []
        for tid, data in sorted(entry["techniques"].items()):
            indicated = " indicated" if tactic == "TA0001" else ""
            cells.append(
                '<a class="tech-cell%s" href="%s" target="_blank" rel="noopener" '
                'title="%s findings">'
                '<span class="mono tech-id">%s</span>'
                '<span class="tech-name">%s</span>'
                '<span class="c num">%d</span></a>'
                % (indicated, mitre.technique_url(tid), data["count"],
                   _esc(tid), _esc(data["name"]), data["count"])
            )
        cols.append(
            '<div class="matrix-col"><div class="matrix-tactic">'
            '<span class="mono">%s</span> %s</div>%s</div>'
            % (_esc(tactic), _esc(entry["name"]), "".join(cells))
        )
    return '<div class="matrix">%s</div>' % "".join(cols)


def _osint(assessment: Assessment) -> str:
    a = assessment.assets
    cards = []
    if a.waf:
        cards.append(
            '<div class="card"><h3>WAF / Edge</h3><div class="pill-list">'
            '<span class="pill">%s</span></div></div>' % _esc(a.waf)
        )
    if a.subdomains:
        items = "".join("<li>%s</li>" % _esc(s) for s in a.subdomains[:200])
        cards.append(
            '<div class="card"><h3>Subdomains (%d)</h3><ul>%s</ul></div>'
            % (len(a.subdomains), items)
        )
    if a.emails:
        items = "".join("<li>%s</li>" % _esc(e) for e in a.emails[:100])
        cards.append(
            '<div class="card"><h3>Emails (%d)</h3><ul>%s</ul></div>'
            % (len(a.emails), items)
        )
    if not cards:
        return '<div class="empty-hint">No OSINT assets collected.</div>'
    return '<div class="cards">%s</div>' % "".join(cards)


def _guidance(findings: List[Finding]) -> str:
    actionable = [f for f in findings if f.severity >= Severity.HIGH]
    if not actionable:
        return (
            '<div class="empty-hint">No high or critical findings require exploitation '
            "guidance. Focus on hardening the attack surface below.</div>"
        )
    items = []
    for f in actionable[:40]:
        summary, detail = None, None
        for cve in f.cves:
            if cve.upper() in _GUIDANCE:
                summary, detail = _GUIDANCE[cve.upper()]
                break
        if not detail:
            detail = (
                "Confirmed %s finding. Validate manually and correlate with Exploit-DB / "
                "searchsploit and vendor advisories before acting. Exploitation itself is "
                "out of scope for this recon tool." % f.severity.label
            )
        loc = _esc(f.host or "")
        if f.port:
            loc += ":" + str(f.port)
        techs = " ".join(_esc(t.get("technique", "")) for t in f.mitre)
        crit_cls = " crit" if f.severity == Severity.CRITICAL else ""
        head = _esc(summary) if summary else _esc(f.title)
        items.append(
            '<div class="guidance-item%s"><h3>%s %s</h3>'
            '<div class="gmeta"><span>%s</span><span>%s</span>'
            '<span class="roe-tag">authorized ROE only</span></div>'
            "<p>%s</p></div>"
            % (crit_cls, _sev_chip(f.severity), head, loc or "&mdash;",
               techs or "", _esc(detail))
        )
    return "".join(items)


def _recommendations(assessment: Assessment) -> str:
    findings = assessment.findings
    recs = []
    counts = _severity_counts(findings)
    if counts["critical"]:
        recs.append(("Remediate critical findings now",
                     "Patch or isolate the %d critical issue(s) immediately; they are the "
                     "highest-probability entry points." % counts["critical"]))
    if counts["high"]:
        recs.append(("Prioritize high-severity patching",
                     "Establish an SLA to remediate the %d high-severity issue(s) within days."
                     % counts["high"]))
    crit_ports = sorted({s.port for h in assessment.hosts for s in h.services if s.is_critical})
    if crit_ports:
        recs.append(("Reduce exposed critical services",
                     "Restrict or firewall exposed management/database ports (%s). Disable "
                     "legacy protocols such as SMBv1 and Telnet." %
                     ", ".join(str(p) for p in crit_ports)))
    if assessment.assets.waf:
        recs.append(("WAF present — tune assumptions",
                     "A %s WAF was detected; validate that findings are not false positives "
                     "and that the WAF is not the only control." % assessment.assets.waf))
    total_ports = sum(len(h.services) for h in assessment.hosts)
    if total_ports > 10:
        recs.append(("Shrink the attack surface",
                     "%d open services were observed. Decommission unused services and apply "
                     "least-exposure network segmentation." % total_ports))
    recs.append(("Strengthen authentication",
                 "Enforce MFA on remote-access and administrative services; replace default "
                 "credentials."))
    recs.append(("Re-test after remediation",
                 "Re-run this assessment once fixes land to confirm closure and catch "
                 "regressions."))
    return "".join(
        '<div class="rec"><b>%s</b><p>%s</p></div>' % (_esc(t), _esc(d)) for t, d in recs
    )


# --------------------------------------------------------------------------- #
# Public renderers
# --------------------------------------------------------------------------- #
def _summary_dict(assessment: Assessment) -> Dict:
    counts = _severity_counts(assessment.findings)
    counts["ports"] = sum(len(h.services) for h in assessment.hosts)
    counts["subdomains"] = len(assessment.assets.subdomains)
    return counts


def render_json(assessment: Assessment) -> str:
    data = assessment.to_dict()
    data["risk_score"] = sev.risk_score(assessment.findings)
    data["risk_level"] = _risk_level(data["risk_score"])
    data["summary"] = _summary_dict(assessment)
    data["generated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return json.dumps(data, indent=2, ensure_ascii=False)


def render_navigator(assessment: Assessment) -> str:
    """ATT&CK Navigator layer JSON (loadable at mitre-attack.github.io/attack-navigator)."""
    layer = mitre.navigator_layer(
        assessment.findings, name="security-scanner: %s" % (assessment.target or "target")
    )
    return json.dumps(layer, indent=2, ensure_ascii=False)


def render_markdown(assessment: Assessment) -> str:
    risk = sev.risk_score(assessment.findings)
    counts = _severity_counts(assessment.findings)
    lines = [
        "# Red Team Assessment — %s" % assessment.target,
        "",
        "- **Target:** %s" % assessment.target,
    ]
    if assessment.url:
        lines.append("- **URL:** %s" % assessment.url)
    if assessment.domain:
        lines.append("- **Domain:** %s" % assessment.domain)
    lines += [
        "- **Mode:** %s" % assessment.scan_mode,
        "- **Date:** %s" % datetime.now().strftime("%Y-%m-%d %H:%M"),
        "- **Risk score:** %d/100 (%s)" % (risk, _risk_level(risk).upper()),
        "",
        "## Summary",
        "",
        "| Critical | High | Medium | Low | Info |",
        "|---|---|---|---|---|",
        "| %d | %d | %d | %d | %d |" % (counts["critical"], counts["high"],
                                        counts["medium"], counts["low"], counts["info"]),
        "",
        "## Findings",
        "",
    ]
    if assessment.findings:
        for f in assessment.findings:
            loc = f.host or ""
            if f.port:
                loc += ":" + str(f.port)
            cves = (" — " + ", ".join(f.cves)) if f.cves else ""
            techs = (" [" + ", ".join(t.get("technique", "") for t in f.mitre) + "]") if f.mitre else ""
            lines.append("- **[%s]** %s (`%s`, %s)%s%s"
                         % (f.severity.label.upper(), f.title, loc or "n/a", f.source or "?", cves, techs))
    else:
        lines.append("_No findings parsed._")
    lines += ["", "## Attack Surface", ""]
    for host in assessment.hosts:
        for svc in host.services:
            flag = " *(critical port)*" if svc.is_critical else ""
            lines.append("- `%s` %s/%s %s %s%s"
                         % (host.ip or assessment.target, svc.port, svc.proto,
                            svc.name or "", svc.version or "", flag))
    return "\n".join(lines) + "\n"


def render_html(assessment: Assessment) -> str:
    risk = sev.risk_score(assessment.findings)
    level = _risk_level(risk)
    counts = _severity_counts(assessment.findings)
    total_findings = len(assessment.findings)
    total_ports = sum(len(h.services) for h in assessment.hosts)
    n_subs = len(assessment.assets.subdomains)
    tactics_touched = len({t.get("technique") for f in assessment.findings for t in f.mitre if t.get("technique")})

    styles = _load_asset("styles.css")
    app_js = _load_asset("app.js")

    # Embedded machine-readable data (escape < > & so it can't break out of <script>).
    def _script_safe(text: str) -> str:
        return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")

    payload_safe = _script_safe(render_json(assessment))
    navigator_safe = _script_safe(render_navigator(assessment))
    markdown_safe = _esc(render_markdown(assessment))

    dossier = ['<div><span class="k">Target</span><span class="v">%s</span></div>' % _esc(assessment.target)]
    if assessment.url:
        dossier.append('<div><span class="k">URL</span><span class="v">%s</span></div>' % _esc(assessment.url))
    if assessment.domain:
        dossier.append('<div><span class="k">Domain</span><span class="v">%s</span></div>' % _esc(assessment.domain))
    dossier.append('<div><span class="k">Mode</span><span class="v">%s</span></div>' % _esc(assessment.scan_mode))
    dossier.append('<div><span class="k">Date</span><span class="v">%s</span></div>'
                   % _esc(datetime.now().strftime("%Y-%m-%d %H:%M")))

    statusline = (
        '<span class="stat"><b>%d</b> CRIT</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> HIGH</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> MED</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> LOW</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> INFO</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> PORTS</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> SUBDOMAINS</span><span class="sep">·</span>'
        '<span class="stat"><b>%d</b> ATT&amp;CK</span>'
        % (counts["critical"], counts["high"], counts["medium"], counts["low"],
           counts["info"], total_ports, n_subs, tactics_touched)
    )

    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        '<meta name="color-scheme" content="light dark">\n'
        "<title>Red Team Report — %(target)s</title>\n"
        "<style>%(styles)s</style>\n</head>\n<body>\n"
        '<div class="roe">Authorized assessment · Red team · Handle per rules of engagement</div>\n'
        '<header class="masthead wrap">\n'
        '<div class="masthead-id"><div class="eyebrow">Red Team Assessment // Field Report</div>'
        "<h1>%(target)s</h1><div class=\"dossier\">%(dossier)s</div></div>\n"
        '<div class="masthead-side">%(gauge)s'
        '<button class="theme-toggle" type="button">☾ Dark</button></div>\n'
        "</header>\n"
        '<div class="statusline wrap">%(statusline)s</div>\n'
        "%(attack)s\n"
        '<main class="layout wrap">\n%(spine)s\n<div class="content">\n'
        '<section id="findings"><div class="section-head"><h2><span class="idx">01</span>Findings</h2>'
        '<span class="meta">%(nfind)d total</span></div>%(findings)s</section>\n'
        '<section id="attack"><div class="section-head"><h2><span class="idx">02</span>ATT&amp;CK Coverage</h2>'
        '<button class="btn" id="export-navigator">Export ATT&amp;CK Layer</button></div>%(matrix)s</section>\n'
        '<section id="surface"><div class="section-head"><h2><span class="idx">03</span>Attack Surface</h2>'
        '<span class="meta">%(nports)d services</span></div>%(surface)s</section>\n'
        '<section id="osint"><div class="section-head"><h2><span class="idx">04</span>OSINT &amp; Assets</h2></div>%(osint)s</section>\n'
        '<section id="guidance"><div class="section-head"><h2><span class="idx">05</span>Exploitation Guidance</h2>'
        '<span class="meta">indication only · authorized ROE</span></div>%(guidance)s</section>\n'
        '<section id="recommendations"><div class="section-head"><h2><span class="idx">06</span>Recommendations</h2></div>%(recs)s</section>\n'
        "</div>\n</main>\n"
        '<footer class="foot wrap"><span>Security Scanner v%(version)s · Red Team Field Report</span>'
        "<span>Generated %(gen)s · Authorized testing only</span></footer>\n"
        '<script id="report-data" type="application/json">%(payload)s</script>\n'
        '<script id="navigator-data" type="application/json">%(navigator)s</script>\n'
        '<pre id="markdown-source" hidden>%(markdown)s</pre>\n'
        "<script>%(app)s</script>\n</body>\n</html>\n"
        % {
            "target": _esc(assessment.target),
            "styles": styles,
            "dossier": "".join(dossier),
            "gauge": _gauge(risk, level),
            "statusline": statusline,
            "attack": _attack_strip(assessment.findings),
            "spine": _spine(counts, total_findings),
            "findings": _findings_table(assessment.findings),
            "matrix": _mitre_matrix(assessment.findings),
            "surface": _surface(assessment),
            "osint": _osint(assessment),
            "guidance": _guidance(assessment.findings),
            "recs": _recommendations(assessment),
            "nfind": total_findings,
            "nports": total_ports,
            "version": _esc(assessment.version),
            "gen": _esc(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "payload": payload_safe,
            "navigator": navigator_safe,
            "markdown": markdown_safe,
            "app": app_js,
        }
    )
