"""Parse OSINT artifacts: subdomains, emails, WAF detection."""
from __future__ import annotations

import re
from typing import List, Optional

_EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@[A-Za-z0-9.\-]+\.[A-Za-z]{2,}")
_DOMAIN_RE = re.compile(r"^[A-Za-z0-9]([A-Za-z0-9.\-]*[A-Za-z0-9])?\.[A-Za-z]{2,}$")
_WAF_RE = re.compile(r"is behind\s+(.+?)\s+WAF", re.IGNORECASE)


def parse_subdomains(text: Optional[str]) -> List[str]:
    subs: List[str] = []
    for raw in (text or "").splitlines():
        line = raw.strip().lower()
        if not line or line.startswith(("#", "=", "total", "top ")):
            continue
        if "failed" in line or " " in line:
            continue
        if _DOMAIN_RE.match(line) and line not in subs:
            subs.append(line)
    return subs


def parse_emails(text: Optional[str]) -> List[str]:
    found: List[str] = []
    for match in _EMAIL_RE.findall(text or ""):
        if match not in found:
            found.append(match)
    return found


def parse_waf(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    match = _WAF_RE.search(text)
    if match:
        return match.group(1).strip()
    return None
