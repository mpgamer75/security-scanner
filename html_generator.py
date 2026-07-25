#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Backward-compatible entry point for report generation.

Usage (unchanged, as called from `security`):
    html_generator.py <outdir> <target> <url> <domain> <scan_mode>

Delegates to the `report` package: it parses the raw tool output under
<outdir>/ into a normalized findings model and writes a self-contained,
offline HTML report plus machine-readable JSON and Markdown.

This file is intentionally thin — the real logic lives in report/ so it can be
unit-tested. The `report/` package must sit next to this file when installed.
"""
import os
import sys

# Make the sibling `report/` package importable no matter the working directory
# (the scanner invokes this from inside a scan-output directory).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from report import collect, render  # noqa: E402


def _clean(value: str) -> str:
    return "" if value in ("NONE", "None", "") else value


def main(argv):
    if len(argv) < 6:
        print("Usage: html_generator.py <outdir> <target> <url> <domain> <scan_mode>")
        return 1

    outdir = argv[1]
    target = argv[2]
    url = _clean(argv[3])
    domain = _clean(argv[4])
    scan_mode = argv[5]

    assessment = collect.build_assessment(outdir, target, url, domain, scan_mode)

    reports_dir = os.path.join(outdir, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    html_path = os.path.join(reports_dir, "assessment.html")
    json_path = os.path.join(reports_dir, "assessment.json")
    findings_path = os.path.join(reports_dir, "findings.json")
    md_path = os.path.join(reports_dir, "assessment.md")
    nav_path = os.path.join(reports_dir, "navigator.json")

    structured_json = render.render_json(assessment)

    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(render.render_html(assessment))
    with open(json_path, "w", encoding="utf-8") as handle:
        handle.write(structured_json)
    # findings.json is the machine-readable contract from the plan — the same
    # normalized model as assessment.json under its documented name.
    with open(findings_path, "w", encoding="utf-8") as handle:
        handle.write(structured_json)
    with open(md_path, "w", encoding="utf-8") as handle:
        handle.write(render.render_markdown(assessment))
    with open(nav_path, "w", encoding="utf-8") as handle:
        handle.write(render.render_navigator(assessment))

    findings = len(assessment.findings)
    print("[SUCCESS] HTML Report: %s (%d findings)" % (html_path, findings))
    print("[INFO] JSON: %s" % json_path)
    print("[INFO] findings.json: %s" % findings_path)
    print("[INFO] Markdown: %s" % md_path)
    print("[INFO] ATT&CK Navigator layer: %s" % nav_path)
    print("[INFO] Open in browser: file://%s" % os.path.abspath(html_path))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception as exc:  # top-level guard: never crash the scan over a report
        import traceback

        print("[ERROR] HTML report generation failed: %s" % exc, file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
