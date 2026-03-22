#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Scanner HTML Report Generator v2.0
Professional, corporate-grade HTML report with modern UX/UI
"""

import sys
import html
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional

VERSION = "2.4.0"


def generate_html_report(outdir: str, target: str, url: str, domain: str, scan_mode: str) -> str:
    """Generate a professional, enterprise-grade HTML report"""

    # Escape all user-controlled inputs to prevent XSS
    safe_target = html.escape(target, quote=True)
    safe_url = html.escape(url, quote=True) if url and url != 'NONE' else ''
    safe_domain = html.escape(domain, quote=True) if domain and domain != 'NONE' else ''
    safe_scan_mode = html.escape(scan_mode, quote=True)

    # Read statistics from files with error handling
    stats = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'ports': 0,
        'subs': 0
    }

    # Count vulnerabilities with improved detection
    files = {
        'nmap_vulns': f'{outdir}/network/nmap_vulns.txt',
        'nmap_critical': f'{outdir}/network/nmap_critical_vulns.txt',
        'nuclei': f'{outdir}/web/nuclei.txt',
        'nikto': f'{outdir}/web/nikto.txt',
        'nmap_ports': f'{outdir}/network/nmap_ports.txt',
        'subdomains': f'{outdir}/osint/all_subdomains.txt'
    }

    for key, filepath in files.items():
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                if key == 'nmap_vulns':
                    stats['critical'] += content.lower().count('vulnerable')
                    stats['critical'] += len(re.findall(r'CVE-\d{4}-\d{4,7}', content, re.IGNORECASE))
                elif key == 'nmap_critical':
                    stats['high'] += content.lower().count('critical')
                    stats['critical'] += content.lower().count('ms17-010')
                    stats['critical'] += content.lower().count('eternalblue')
                elif key == 'nuclei':
                    stats['medium'] += content.lower().count('[medium]')
                    stats['high'] += content.lower().count('[high]')
                    stats['critical'] += content.lower().count('[critical]')
                elif key == 'nikto':
                    stats['medium'] += content.lower().count('osvdb')
                    stats['high'] += content.lower().count('dangerous')
                elif key == 'nmap_ports':
                    stats['ports'] = len([l for l in content.splitlines() if 'open' in l.lower()])
                elif key == 'subdomains':
                    stats['subs'] = len([l for l in content.splitlines() if l.strip() and not l.startswith('#')])
        except FileNotFoundError:
            continue
        except Exception as e:
            print(f"[WARNING] Error reading {filepath}: {e}", file=sys.stderr)

    # Calculate risk score (0-100)
    risk_score = min(100, stats['critical'] * 10 + stats['high'] * 5 + stats['medium'] * 2 + stats['low'] * 1)

    if risk_score >= 70:
        risk_level = "CRITICAL"
        risk_color = "#ff3b3b"
    elif risk_score >= 40:
        risk_level = "HIGH"
        risk_color = "#ff8c42"
    elif risk_score >= 20:
        risk_level = "MEDIUM"
        risk_color = "#ffd23f"
    else:
        risk_level = "LOW"
        risk_color = "#3bceac"

    # Read findings with categorization
    network_vulns = []
    web_vulns = []
    services = []
    critical_services = []

    try:
        with open(f'{outdir}/network/nmap_vulns.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line_stripped = line.strip()
                if not line_stripped:  # Skip empty lines
                    continue

                line_upper = line_stripped.upper()

                # Keywords that indicate actual vulnerabilities
                vuln_keywords = ['VULNERABLE', 'CVE-', 'EXPLOIT', 'CRITICAL', 'HIGH RISK', 'SEVERITY']

                # Keywords that indicate scan status/noise (not vulnerabilities)
                noise_keywords = ['SCANNING', 'STARTING', 'NSE:', 'SCRIPT EXECUTION', 'ATTEMPTING', 'TRYING', 'CHECKING']

                # Check if line contains vulnerability keywords
                has_vuln_keyword = any(keyword in line_upper for keyword in vuln_keywords)

                # Check if line is just noise
                is_noise = any(noise in line_upper for noise in noise_keywords)

                # Keep line if it has vulnerability keywords AND is not noise
                if has_vuln_keyword and not is_noise:
                    network_vulns.append(line_stripped)
                    if len(network_vulns) >= 100:
                        break
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/web/nuclei.txt', 'r', encoding='utf-8', errors='ignore') as f:
            web_vulns = [line.strip() for line in f if line.strip() and not line.startswith('#')][:100]
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/network/nmap_services.txt', 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                if 'open' in line.lower():
                    services.append(line.strip())
                    # Detect critical services
                    if any(port in line.lower() for port in ['445', '3389', '22', '21', '23', '1433', '3306']):
                        critical_services.append(line.strip())
                    if len(services) >= 50:
                        break
    except FileNotFoundError:
        pass

    # Generate Critical Services section before main HTML to avoid f-string nesting issues
    critical_services_html = ''
    if critical_services:
        critical_services_html = f'''<div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon">&#9888;</span>
                        Critical Services Detected
                    </h2>
                </div>
                <div class="findings-grid">
                    {_generate_findings(critical_services[:10], None, "critical")}
                </div>
            </div>'''

    # Generate HTML with professional design
    report_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Report - {safe_target}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            /* Professional Color Palette */
            --bg-primary: #1a1d29;
            --bg-secondary: #242837;
            --bg-tertiary: #2d3142;
            --bg-elevated: rgba(255, 255, 255, 0.05);
            --bg-elevated-hover: rgba(255, 255, 255, 0.08);
            
            /* Corporate Orange Accent */
            --accent-primary: #ff6b35;
            --accent-primary-dark: #e55a2b;
            --accent-secondary: #00d4ff;
            
            /* Semantic Colors */
            --critical: #ff3b3b;
            --high: #ff8c42;
            --medium: #ffd23f;
            --low: #3bceac;
            --info: #5b9cff;
            
            /* Text Colors - Optimized Contrast */
            --text-primary: #ffffff;
            --text-secondary: #b8c5d6;
            --text-tertiary: #7a8599;
            
            /* UI Elements */
            --border-subtle: rgba(255, 255, 255, 0.08);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.4);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.5);
        }}

        /* Light Mode Variables */
        [data-theme="light"] {{
            --bg-primary: #f0f2f5;
            --bg-secondary: #ffffff;
            --bg-tertiary: #e8eaf0;
            --bg-elevated: rgba(0, 0, 0, 0.04);
            --bg-elevated-hover: rgba(0, 0, 0, 0.07);
            --text-primary: #1a1d29;
            --text-secondary: #4a5568;
            --text-tertiary: #718096;
            --border-subtle: rgba(0, 0, 0, 0.1);
            --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
            --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
            --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
        }}

        /* System preference: respect prefers-color-scheme unless overridden */
        @media (prefers-color-scheme: light) {{
            :root:not([data-theme="dark"]) {{
                --bg-primary: #f0f2f5;
                --bg-secondary: #ffffff;
                --bg-tertiary: #e8eaf0;
                --bg-elevated: rgba(0, 0, 0, 0.04);
                --bg-elevated-hover: rgba(0, 0, 0, 0.07);
                --text-primary: #1a1d29;
                --text-secondary: #4a5568;
                --text-tertiary: #718096;
                --border-subtle: rgba(0, 0, 0, 0.1);
                --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.08);
                --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.12);
                --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.16);
            }}
        }}

        /* Scroll progress bar */
        #scroll-progress {{
            position: fixed;
            top: 0;
            left: 0;
            height: 3px;
            width: 0%;
            background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
            z-index: 9999;
            transition: width 0.1s linear;
        }}

        /* Skip navigation for accessibility */
        .skip-nav {{
            position: absolute;
            top: -40px;
            left: 0;
            background: var(--accent-primary);
            color: white;
            padding: 8px 16px;
            text-decoration: none;
            font-weight: 600;
            z-index: 10000;
            border-radius: 0 0 8px 0;
        }}
        .skip-nav:focus {{
            top: 0;
        }}

        /* Theme toggle button */
        .theme-toggle {{
            position: fixed;
            top: 16px;
            right: 16px;
            z-index: 1000;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 24px;
            padding: 8px 14px;
            color: var(--text-primary);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            display: flex;
            align-items: center;
            gap: 6px;
            transition: all 0.2s ease;
            box-shadow: var(--shadow-sm);
        }}
        .theme-toggle:hover {{
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
        }}
        .theme-toggle:focus-visible {{
            outline: 2px solid var(--accent-primary);
            outline-offset: 2px;
        }}

        /* Search bar */
        .search-container {{
            margin-bottom: 24px;
            position: relative;
        }}
        .search-input {{
            width: 100%;
            padding: 12px 16px 12px 44px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 0.95rem;
            font-family: inherit;
            transition: all 0.2s ease;
        }}
        .search-input:focus {{
            outline: none;
            border-color: var(--accent-primary);
            box-shadow: 0 0 0 3px rgba(255, 107, 53, 0.15);
        }}
        .search-icon {{
            position: absolute;
            left: 14px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-tertiary);
            font-size: 1.1rem;
            pointer-events: none;
        }}
        .search-clear {{
            position: absolute;
            right: 12px;
            top: 50%;
            transform: translateY(-50%);
            background: none;
            border: none;
            color: var(--text-tertiary);
            cursor: pointer;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.85rem;
            display: none;
        }}
        .search-clear.visible {{
            display: block;
        }}
        .search-clear:hover {{
            color: var(--text-primary);
        }}

        /* Copy button on findings */
        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 8px;
        }}
        .finding-text {{
            flex: 1;
            white-space: pre-wrap;
            margin: 0;
            font-family: inherit;
            font-size: inherit;
        }}
        .copy-btn {{
            flex-shrink: 0;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            border-radius: 6px;
            color: var(--text-secondary);
            font-size: 0.75rem;
            font-weight: 600;
            padding: 4px 10px;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
        }}
        .copy-btn:hover {{
            background: var(--accent-primary);
            color: white;
            border-color: var(--accent-primary);
        }}
        .copy-btn:focus-visible {{
            outline: 2px solid var(--accent-primary);
            outline-offset: 2px;
        }}

        /* Toast notification */
        .toast {{
            position: fixed;
            bottom: 100px;
            right: 32px;
            background: var(--bg-secondary);
            border: 1px solid var(--border-subtle);
            border-radius: 10px;
            padding: 12px 20px;
            color: var(--text-primary);
            font-size: 0.9rem;
            font-weight: 600;
            box-shadow: var(--shadow-lg);
            z-index: 2000;
            opacity: 0;
            transform: translateY(10px);
            pointer-events: none;
            transition: all 0.3s ease;
        }}
        .toast.show {{
            opacity: 1;
            transform: translateY(0);
            pointer-events: auto;
        }}

        /* Donut chart */
        .donut-chart-container {{
            display: flex;
            align-items: center;
            gap: 32px;
            flex-wrap: wrap;
            margin-top: 16px;
        }}
        .donut-svg {{
            transform: rotate(-90deg);
        }}
        .donut-legend {{
            display: flex;
            flex-direction: column;
            gap: 10px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 10px;
            font-size: 0.9rem;
        }}
        .legend-dot {{
            width: 12px;
            height: 12px;
            border-radius: 50%;
            flex-shrink: 0;
        }}
        .legend-label {{
            color: var(--text-secondary);
        }}
        .legend-value {{
            font-weight: 700;
            color: var(--text-primary);
            margin-left: auto;
            padding-left: 16px;
        }}

        /* Severity filter buttons */
        .severity-filters {{
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
            margin-bottom: 16px;
        }}
        .filter-btn {{
            padding: 6px 16px;
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: 20px;
            color: var(--text-secondary);
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .filter-btn:hover {{
            color: var(--text-primary);
            border-color: currentColor;
        }}
        .filter-btn.active {{
            color: white;
            background: var(--accent-primary);
            border-color: var(--accent-primary);
        }}
        .filter-btn.critical.active {{ background: var(--critical); border-color: var(--critical); }}
        .filter-btn.high.active {{ background: var(--high); border-color: var(--high); color: #1a1d29; }}
        .filter-btn.medium.active {{ background: var(--medium); border-color: var(--medium); color: #1a1d29; }}
        .filter-btn.low.active {{ background: var(--low); border-color: var(--low); color: #1a1d29; }}

        /* Focus visible for accessibility */
        :focus-visible {{
            outline: 2px solid var(--accent-primary);
            outline-offset: 2px;
        }}

        /* No results message */
        .no-results {{
            text-align: center;
            padding: 32px;
            color: var(--text-tertiary);
            font-style: italic;
            display: none;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            line-height: 1.6;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
        }}

        /* Animations */
        @keyframes fadeInUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes slideIn {{
            from {{
                opacity: 0;
                transform: translateX(-20px);
            }}
            to {{
                opacity: 1;
                transform: translateX(0);
            }}
        }}

        @keyframes shimmer {{
            0% {{ background-position: -1000px 0; }}
            100% {{ background-position: 1000px 0; }}
        }}

        /* Header - Compact & Professional */
        .header {{
            background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-tertiary) 100%);
            border-bottom: 2px solid var(--accent-primary);
            padding: 40px 20px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 200%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 107, 53, 0.1), transparent);
            animation: shimmer 3s infinite;
        }}

        .header-content {{
            max-width: 1400px;
            margin: 0 auto;
            position: relative;
            z-index: 1;
        }}

        .header h1 {{
            font-size: clamp(2rem, 5vw, 2.5rem);
            font-weight: 800;
            margin-bottom: 8px;
            background: linear-gradient(135deg, var(--text-primary) 0%, var(--accent-primary) 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }}

        .header-meta {{
            display: flex;
            justify-content: center;
            gap: 24px;
            flex-wrap: wrap;
            margin-top: 16px;
        }}

        .meta-item {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
        }}

        .meta-item strong {{
            color: var(--text-primary);
        }}

        /* Container */
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 40px 20px;
        }}

        /* Risk Score Banner */
        .risk-banner {{
            background: var(--bg-elevated);
            border: 2px solid {risk_color};
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 40px;
            text-align: center;
            box-shadow: 0 0 40px rgba(0, 0, 0, 0.4);
            animation: fadeInUp 0.6s ease-out;
        }}

        .risk-score {{
            font-size: 4rem;
            font-weight: 900;
            color: {risk_color};
            line-height: 1;
            margin-bottom: 12px;
        }}

        .risk-level {{
            display: inline-block;
            background: {risk_color};
            color: white;
            padding: 8px 24px;
            border-radius: 24px;
            font-weight: 700;
            font-size: 1.1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}

        /* Stats Grid */
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            margin-bottom: 48px;
        }}

        .stat-card {{
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 28px 24px;
            text-align: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
            position: relative;
            overflow: hidden;
            animation: fadeInUp 0.6s ease-out;
            animation-fill-mode: both;
        }}

        .stat-card:nth-child(1) {{ animation-delay: 0.1s; }}
        .stat-card:nth-child(2) {{ animation-delay: 0.2s; }}
        .stat-card:nth-child(3) {{ animation-delay: 0.3s; }}
        .stat-card:nth-child(4) {{ animation-delay: 0.4s; }}
        .stat-card:nth-child(5) {{ animation-delay: 0.5s; }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: currentColor;
            transform: scaleX(0);
            transition: transform 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: var(--shadow-lg);
            border-color: currentColor;
        }}

        .stat-card:hover::before {{
            transform: scaleX(1);
        }}

        .stat-icon {{
            font-size: 2rem;
            margin-bottom: 12px;
            opacity: 0.8;
        }}

        .stat-number {{
            font-size: 3.5rem;
            font-weight: 800;
            line-height: 1;
            margin-bottom: 8px;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover .stat-number {{
            transform: scale(1.1);
        }}

        .stat-label {{
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--text-secondary);
        }}

        .stat-card.critical {{ color: var(--critical); }}
        .stat-card.high {{ color: var(--high); }}
        .stat-card.medium {{ color: var(--medium); }}
        .stat-card.info {{ color: var(--info); }}

        /* Tabs Navigation */
        .tabs {{
            display: flex;
            gap: 8px;
            margin-bottom: 32px;
            overflow-x: auto;
            padding: 4px;
            background: var(--bg-elevated);
            border-radius: 12px;
            border: 1px solid var(--border-subtle);
        }}

        .tab-button {{
            padding: 12px 24px;
            background: transparent;
            border: none;
            border-radius: 8px;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.95rem;
            cursor: pointer;
            transition: all 0.2s ease;
            white-space: nowrap;
            position: relative;
        }}

        .tab-button:hover {{
            color: var(--text-primary);
            background: var(--bg-elevated-hover);
        }}

        .tab-button.active {{
            background: var(--accent-primary);
            color: white;
            box-shadow: var(--shadow-sm);
        }}

        .tab-badge {{
            display: inline-block;
            background: var(--accent-primary);
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            margin-left: 6px;
        }}

        .tab-button.active .tab-badge {{
            background: rgba(255, 255, 255, 0.2);
        }}

        /* Tab Content */
        .tab-content {{
            display: none;
            animation: fadeInUp 0.4s ease-out;
        }}

        .tab-content.active {{
            display: block;
        }}

        /* Section */
        .section {{
            background: var(--bg-elevated);
            border: 1px solid var(--border-subtle);
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
        }}

        .section-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 2px solid var(--border-subtle);
        }}

        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section-icon {{
            font-size: 1.8rem;
        }}

        .section-actions {{
            display: flex;
            gap: 8px;
        }}

        .btn {{
            padding: 8px 16px;
            background: var(--bg-tertiary);
            border: 1px solid var(--border-subtle);
            border-radius: 8px;
            color: var(--text-primary);
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
        }}

        .btn:hover {{
            background: var(--accent-primary);
            border-color: var(--accent-primary);
            transform: translateY(-2px);
        }}

        /* Findings List */
        .findings-grid {{
            display: grid;
            gap: 12px;
        }}

        .finding-item {{
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-secondary);
            border-radius: 8px;
            padding: 16px 20px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            transition: all 0.2s ease;
            cursor: default;
            animation: slideIn 0.3s ease-out;
        }}

        .finding-item:hover {{
            transform: translateX(8px);
            box-shadow: var(--shadow-md);
        }}

        .finding-item.critical {{
            border-left-color: var(--critical);
            background: linear-gradient(90deg, rgba(255, 59, 59, 0.1), transparent);
        }}

        .finding-item.high {{
            border-left-color: var(--high);
            background: linear-gradient(90deg, rgba(255, 140, 66, 0.1), transparent);
        }}

        .finding-item.medium {{
            border-left-color: var(--medium);
            background: linear-gradient(90deg, rgba(255, 210, 63, 0.1), transparent);
        }}

        .empty-state {{
            text-align: center;
            padding: 48px 24px;
            color: var(--text-tertiary);
        }}

        .empty-state-icon {{
            font-size: 4rem;
            margin-bottom: 16px;
            opacity: 0.3;
        }}

        .empty-state-text {{
            font-size: 1.1rem;
            font-weight: 500;
        }}

        /* Services Table */
        .services-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}

        .services-table thead {{
            background: var(--bg-tertiary);
        }}

        .services-table th {{
            padding: 12px 16px;
            text-align: left;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            color: var(--accent-primary);
            border-bottom: 2px solid var(--border-subtle);
        }}

        .services-table td {{
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-subtle);
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.85rem;
        }}

        .services-table tr {{
            transition: background 0.2s ease;
        }}

        .services-table tbody tr:hover {{
            background: var(--bg-elevated-hover);
        }}

        .service-badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .service-badge.critical {{
            background: rgba(255, 59, 59, 0.2);
            color: var(--critical);
        }}

        /* Recommendations */
        .recommendations-grid {{
            display: grid;
            gap: 16px;
            margin-top: 24px;
        }}

        .recommendation {{
            background: linear-gradient(135deg, rgba(0, 212, 255, 0.1), rgba(91, 156, 255, 0.05));
            border-left: 4px solid var(--accent-secondary);
            border-radius: 12px;
            padding: 20px 24px;
            transition: all 0.2s ease;
        }}

        .recommendation:hover {{
            transform: translateX(4px);
            box-shadow: var(--shadow-md);
        }}

        .recommendation-title {{
            font-weight: 700;
            font-size: 1.05rem;
            color: var(--accent-secondary);
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        .recommendation-text {{
            color: var(--text-secondary);
            line-height: 1.6;
        }}

        /* Scroll to Top Button */
        .scroll-top {{
            position: fixed;
            bottom: 32px;
            right: 32px;
            width: 56px;
            height: 56px;
            background: var(--accent-primary);
            color: white;
            border: none;
            border-radius: 50%;
            font-size: 24px;
            cursor: pointer;
            box-shadow: var(--shadow-lg);
            transition: all 0.3s ease;
            opacity: 0;
            pointer-events: none;
            z-index: 1000;
        }}

        .scroll-top.visible {{
            opacity: 1;
            pointer-events: auto;
        }}

        .scroll-top:hover {{
            background: var(--accent-primary-dark);
            transform: translateY(-4px);
        }}

        /* Footer */
        .footer {{
            text-align: center;
            padding: 40px 20px;
            color: var(--text-tertiary);
            border-top: 1px solid var(--border-subtle);
            margin-top: 48px;
        }}

        .footer p {{
            margin: 8px 0;
        }}

        /* Responsive Design */
        @media (max-width: 768px) {{
            .header {{
                padding: 32px 16px;
            }}

            .header h1 {{
                font-size: 1.75rem;
            }}

            .header-meta {{
                flex-direction: column;
                gap: 8px;
            }}

            .container {{
                padding: 24px 16px;
            }}

            .stats-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}

            .stat-number {{
                font-size: 2.5rem;
            }}

            .tabs {{
                overflow-x: scroll;
            }}

            .section {{
                padding: 24px 16px;
            }}

            .section-header {{
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }}

            .scroll-top {{
                bottom: 20px;
                right: 20px;
                width: 48px;
                height: 48px;
            }}
        }}

        /* Print Styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            
            .tabs,
            .scroll-top,
            .btn {{
                display: none !important;
            }}

            .tab-content {{
                display: block !important;
            }}

            .section {{
                page-break-inside: avoid;
            }}
        }}
    </style>
</head>
<body>
    <!-- Scroll Progress Bar -->
    <div id="scroll-progress" role="progressbar" aria-label="Page scroll progress"></div>

    <!-- Skip Navigation (Accessibility) -->
    <a href="#main-content" class="skip-nav">Skip to main content</a>

    <!-- Theme Toggle -->
    <button class="theme-toggle" id="themeToggle" aria-label="Toggle light/dark mode">
        <span id="themeIcon">☀️</span> <span id="themeLabel">Light</span>
    </button>

    <!-- Scroll to Top Button -->
    <button class="scroll-top" id="scrollTop" aria-label="Scroll to top">↑</button>

    <!-- Toast Notification -->
    <div class="toast" id="toast" role="status" aria-live="polite"></div>

    <!-- Header -->
    <header class="header" role="banner">
        <div class="header-content">
            <h1>Security Report</h1>
            <div class="header-meta">
                <div class="meta-item">
                    <span>🎯</span>
                    <strong>Target:</strong> {safe_target}
                </div>
                {f'<div class="meta-item"><span>🌐</span><strong>URL:</strong> {safe_url}</div>' if safe_url else ''}
                {f'<div class="meta-item"><span>🔗</span><strong>Domain:</strong> {safe_domain}</div>' if safe_domain else ''}
                <div class="meta-item">
                    <span>📅</span>
                    <strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M')}
                </div>
                <div class="meta-item">
                    <span>⚡</span>
                    <strong>Mode:</strong> {safe_scan_mode}
                </div>
            </div>
        </div>
    </header>

    <!-- Main Container -->
    <main class="container" id="main-content" role="main">
        <!-- Risk Score Banner -->
        <div class="risk-banner">
            <div class="risk-score">{risk_score}<span style="font-size: 2rem;">/100</span></div>
            <div class="risk-level">{risk_level} RISK</div>
        </div>

        <!-- Stats Grid -->
        <div class="stats-grid" role="region" aria-label="Scan statistics">
            <div class="stat-card critical">
                <div class="stat-icon" aria-hidden="true">🔴</div>
                <div class="stat-number" data-target="{stats['critical']}">{stats['critical']}</div>
                <div class="stat-label">Critical Issues</div>
            </div>
            <div class="stat-card high">
                <div class="stat-icon" aria-hidden="true">🟠</div>
                <div class="stat-number" data-target="{stats['high']}">{stats['high']}</div>
                <div class="stat-label">High Risk</div>
            </div>
            <div class="stat-card medium">
                <div class="stat-icon" aria-hidden="true">🟡</div>
                <div class="stat-number" data-target="{stats['medium']}">{stats['medium']}</div>
                <div class="stat-label">Medium Risk</div>
            </div>
            <div class="stat-card info">
                <div class="stat-icon" aria-hidden="true">🔵</div>
                <div class="stat-number" data-target="{stats['ports']}">{stats['ports']}</div>
                <div class="stat-label">Open Ports</div>
            </div>
            <div class="stat-card info">
                <div class="stat-icon" aria-hidden="true">🌐</div>
                <div class="stat-number" data-target="{stats['subs']}">{stats['subs']}</div>
                <div class="stat-label">Subdomains</div>
            </div>
        </div>

        <!-- Search Bar -->
        <div class="search-container" role="search">
            <span class="search-icon" aria-hidden="true">🔍</span>
            <input type="search" class="search-input" id="searchInput"
                   placeholder="Search findings…" aria-label="Search findings">
            <button class="search-clear" id="searchClear" aria-label="Clear search">✕</button>
        </div>

        <!-- Tabs Navigation -->
        <div class="tabs" role="tablist" aria-label="Report sections">
            <button class="tab-button active" role="tab" aria-selected="true"
                    aria-controls="overview" data-tab="overview" id="tab-overview">
                📊 Overview
            </button>
            <button class="tab-button" role="tab" aria-selected="false"
                    aria-controls="network" data-tab="network" id="tab-network">
                🔒 Network
                {f'<span class="tab-badge" aria-label="{len(network_vulns)} network findings">{len(network_vulns)}</span>' if network_vulns else ''}
            </button>
            <button class="tab-button" role="tab" aria-selected="false"
                    aria-controls="web" data-tab="web" id="tab-web">
                🌐 Web
                {f'<span class="tab-badge" aria-label="{len(web_vulns)} web findings">{len(web_vulns)}</span>' if web_vulns else ''}
            </button>
            <button class="tab-button" role="tab" aria-selected="false"
                    aria-controls="services" data-tab="services" id="tab-services">
                ⚙️ Services
                {f'<span class="tab-badge" aria-label="{len(services)} services">{len(services)}</span>' if services else ''}
            </button>
            <button class="tab-button" role="tab" aria-selected="false"
                    aria-controls="recommendations" data-tab="recommendations" id="tab-recommendations">
                💡 Recommendations
            </button>
        </div>

        <!-- Tab: Overview -->
        <div class="tab-content active" id="overview"
             role="tabpanel" aria-labelledby="tab-overview" tabindex="0">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon">📈</span>
                        Executive Summary
                    </h2>
                </div>
                <div style="line-height: 1.8; color: var(--text-secondary);">
                    <p style="margin-bottom: 16px;">
                        This security assessment was conducted on <strong style="color: var(--text-primary);">{safe_target}</strong>
                        using automated scanning tools and techniques. The assessment identified 
                        <strong style="color: var(--critical);">{stats['critical']} critical</strong>, 
                        <strong style="color: var(--high);">{stats['high']} high</strong>, and 
                        <strong style="color: var(--medium);">{stats['medium']} medium</strong> severity issues.
                    </p>
                    <p style="margin-bottom: 16px;">
                        The overall risk score of <strong style="color: {risk_color};">{risk_score}/100</strong> indicates a 
                        <strong style="color: {risk_color};">{risk_level}</strong> risk level that requires 
                        {'immediate attention and remediation.' if risk_score >= 70 else 'attention and planned remediation.' if risk_score >= 40 else 'monitoring and standard security practices.'}
                    </p>
                    <p>
                        Key findings include {stats['ports']} open ports, {stats['subs']} discovered subdomains, and 
                        {len(critical_services)} critical services exposed. Detailed findings and recommendations are provided in the subsequent sections.
                    </p>
                </div>
            </div>

            {critical_services_html}

            <!-- Donut Chart: Vulnerability Distribution -->
            {_generate_donut_chart(stats)}
        </div>

        <!-- Tab: Network -->
        <div class="tab-content" id="network"
             role="tabpanel" aria-labelledby="tab-network" tabindex="0">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon" aria-hidden="true">🔒</span>
                        Network Vulnerabilities
                    </h2>
                </div>
                <div class="severity-filters" role="group" aria-label="Filter by severity">
                    <button class="filter-btn active" data-filter="all" data-target="network-findings">All</button>
                    <button class="filter-btn critical" data-filter="critical" data-target="network-findings">🔴 Critical</button>
                    <button class="filter-btn high" data-filter="high" data-target="network-findings">🟠 High</button>
                    <button class="filter-btn medium" data-filter="medium" data-target="network-findings">🟡 Medium</button>
                </div>
                <div class="findings-grid" id="network-findings" role="list" aria-label="Network vulnerability findings">
                    {_generate_findings(network_vulns, "No network vulnerabilities detected or scan not performed. This is a positive security indicator.")}
                </div>
                <p class="no-results" id="network-no-results">No findings match the current filter.</p>
            </div>
        </div>

        <!-- Tab: Web -->
        <div class="tab-content" id="web"
             role="tabpanel" aria-labelledby="tab-web" tabindex="0">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon" aria-hidden="true">🌐</span>
                        Web Application Vulnerabilities
                    </h2>
                </div>
                <div class="severity-filters" role="group" aria-label="Filter by severity">
                    <button class="filter-btn active" data-filter="all" data-target="web-findings">All</button>
                    <button class="filter-btn critical" data-filter="critical" data-target="web-findings">🔴 Critical</button>
                    <button class="filter-btn high" data-filter="high" data-target="web-findings">🟠 High</button>
                    <button class="filter-btn medium" data-filter="medium" data-target="web-findings">🟡 Medium</button>
                </div>
                <div class="findings-grid" id="web-findings" role="list" aria-label="Web vulnerability findings">
                    {_generate_findings(web_vulns, "No web vulnerabilities detected or scan not performed. Continue monitoring for emerging threats.")}
                </div>
                <p class="no-results" id="web-no-results">No findings match the current filter.</p>
            </div>
        </div>

        <!-- Tab: Services -->
        <div class="tab-content" id="services"
             role="tabpanel" aria-labelledby="tab-services" tabindex="0">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon" aria-hidden="true">⚙️</span>
                        Detected Services
                    </h2>
                </div>
                {_generate_services_table(services, critical_services)}
            </div>
        </div>

        <!-- Tab: Recommendations -->
        <div class="tab-content" id="recommendations"
             role="tabpanel" aria-labelledby="tab-recommendations" tabindex="0">
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon">💡</span>
                        Security Recommendations
                    </h2>
                </div>
                <div class="recommendations-grid">
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>🔒</span> Immediate Actions Required
                        </div>
                        <div class="recommendation-text">
                            Address all critical and high-severity vulnerabilities within 24-48 hours. Prioritize publicly exploitable issues and those affecting critical services.
                        </div>
                    </div>
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>🛡️</span> Patch Management
                        </div>
                        <div class="recommendation-text">
                            Implement a comprehensive patch management strategy. Ensure all systems and applications are updated with the latest security patches.
                        </div>
                    </div>
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>🔐</span> Access Control
                        </div>
                        <div class="recommendation-text">
                            Review and strengthen authentication mechanisms. Implement multi-factor authentication (MFA) for all critical systems and administrative access.
                        </div>
                    </div>
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>🚫</span> Service Hardening
                        </div>
                        <div class="recommendation-text">
                            Disable unnecessary services and close unused ports. Apply the principle of least privilege across all systems and applications.
                        </div>
                    </div>
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>📊</span> Continuous Monitoring
                        </div>
                        <div class="recommendation-text">
                            Implement security monitoring and logging. Set up alerts for suspicious activities and conduct regular security assessments.
                        </div>
                    </div>
                    <div class="recommendation">
                        <div class="recommendation-title">
                            <span>🔄</span> Incident Response
                        </div>
                        <div class="recommendation-text">
                            Develop and maintain an incident response plan. Conduct regular drills and ensure team members are trained on security procedures.
                        </div>
                    </div>
                </div>
            </div>

            <div class="section" style="margin-top: 24px;">
                <div class="section-header">
                    <h2 class="section-title">
                        <span class="section-icon">🎯</span>
                        Next Steps for Red Team
                    </h2>
                </div>
                <div style="line-height: 1.8; color: var(--text-secondary);">
                    <ol style="margin-left: 24px;">
                        <li style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">Review Exploit Scripts:</strong> Examine generated scripts in the <code style="background: var(--bg-tertiary); padding: 2px 8px; border-radius: 4px;">exploit/</code> directory</li>
                        <li style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">Test Credentials:</strong> Verify default credentials from the database against detected services</li>
                        <li style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">Manual Validation:</strong> Manually verify automated findings to eliminate false positives</li>
                        <li style="margin-bottom: 12px;"><strong style="color: var(--text-primary);">Exploitation:</strong> With proper authorization, attempt exploitation of confirmed vulnerabilities</li>
                        <li><strong style="color: var(--text-primary);">Documentation:</strong> Maintain detailed documentation of all findings and testing activities</li>
                    </ol>
                </div>
            </div>
        </div>

        <!-- Footer -->
        <footer class="footer">
            <p><strong>Security Scanner v{VERSION}</strong></p>
            <p>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p style="margin-top: 16px; color: var(--text-tertiary);">
                This tool is for authorized security testing only. Unauthorized use is illegal.
            </p>
        </footer>
    </main>

    <script>
        // ============================================================
        // Theme Toggle (Light/Dark Mode)
        // ============================================================
        const themeToggleBtn = document.getElementById('themeToggle');
        const themeIcon = document.getElementById('themeIcon');
        const themeLabel = document.getElementById('themeLabel');
        const htmlEl = document.documentElement;

        const applyTheme = (theme) => {{
            htmlEl.setAttribute('data-theme', theme);
            if (theme === 'light') {{
                themeIcon.textContent = '🌙';
                themeLabel.textContent = 'Dark';
            }} else {{
                themeIcon.textContent = '☀️';
                themeLabel.textContent = 'Light';
            }}
        }};

        // Load saved preference or detect system preference
        const savedTheme = localStorage.getItem('reportTheme');
        if (savedTheme) {{
            applyTheme(savedTheme);
        }} else {{
            const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
            applyTheme(prefersDark ? 'dark' : 'light');
        }}

        themeToggleBtn.addEventListener('click', () => {{
            const current = htmlEl.getAttribute('data-theme') || 'dark';
            const next = current === 'dark' ? 'light' : 'dark';
            applyTheme(next);
            localStorage.setItem('reportTheme', next);
        }});

        // ============================================================
        // Tab Switching with ARIA support
        // ============================================================
        document.querySelectorAll('.tab-button').forEach(button => {{
            button.addEventListener('click', () => {{
                const tabId = button.dataset.tab;

                document.querySelectorAll('.tab-button').forEach(btn => {{
                    btn.classList.remove('active');
                    btn.setAttribute('aria-selected', 'false');
                }});
                button.classList.add('active');
                button.setAttribute('aria-selected', 'true');

                document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
                document.getElementById(tabId).classList.add('active');

                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }});
        }});

        // ============================================================
        // Scroll Progress Bar
        // ============================================================
        const progressBar = document.getElementById('scroll-progress');
        const scrollTopBtn = document.getElementById('scrollTop');

        window.addEventListener('scroll', () => {{
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
            progressBar.style.width = progress + '%';

            if (scrollTop > 300) {{
                scrollTopBtn.classList.add('visible');
            }} else {{
                scrollTopBtn.classList.remove('visible');
            }}
        }});

        scrollTopBtn.addEventListener('click', () => {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});

        // ============================================================
        // Animate Numbers on Load
        // ============================================================
        const animateNumber = (element) => {{
            const target = parseInt(element.dataset.target) || 0;
            if (target === 0) return;
            const duration = 1000;
            const step = target / (duration / 16);
            let current = 0;
            const timer = setInterval(() => {{
                current += step;
                if (current >= target) {{
                    element.textContent = target;
                    clearInterval(timer);
                }} else {{
                    element.textContent = Math.floor(current);
                }}
            }}, 16);
        }};

        const observer = new IntersectionObserver((entries) => {{
            entries.forEach(entry => {{
                if (entry.isIntersecting) {{
                    entry.target.querySelectorAll('.stat-number[data-target]').forEach(num => {{
                        if (!num.classList.contains('animated')) {{
                            animateNumber(num);
                            num.classList.add('animated');
                        }}
                    }});
                    observer.unobserve(entry.target);
                }}
            }});
        }}, {{ threshold: 0.5 }});

        const statsGrid = document.querySelector('.stats-grid');
        if (statsGrid) observer.observe(statsGrid);

        // ============================================================
        // Severity Filter Buttons
        // ============================================================
        document.querySelectorAll('.severity-filters').forEach(filterGroup => {{
            filterGroup.querySelectorAll('.filter-btn').forEach(btn => {{
                btn.addEventListener('click', () => {{
                    const filter = btn.dataset.filter;
                    const targetId = btn.dataset.target;

                    filterGroup.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');

                    const container = document.getElementById(targetId);
                    if (!container) return;
                    const findings = container.querySelectorAll('.finding-item');
                    let visible = 0;

                    findings.forEach(finding => {{
                        const show = filter === 'all' || finding.classList.contains(filter);
                        finding.style.display = show ? '' : 'none';
                        if (show) visible++;
                    }});

                    // Show "no results" message
                    const noResultsId = targetId.replace('-findings', '-no-results');
                    const noResultsEl = document.getElementById(noResultsId);
                    if (noResultsEl) {{
                        noResultsEl.style.display = visible === 0 && findings.length > 0 ? 'block' : 'none';
                    }}
                }});
            }});
        }});

        // ============================================================
        // Copy-to-Clipboard with Toast
        // ============================================================
        const toast = document.getElementById('toast');
        let toastTimer;

        const showToast = (message) => {{
            toast.textContent = message;
            toast.classList.add('show');
            clearTimeout(toastTimer);
            toastTimer = setTimeout(() => toast.classList.remove('show'), 2500);
        }};

        document.querySelectorAll('.copy-btn').forEach(btn => {{
            btn.addEventListener('click', (e) => {{
                e.stopPropagation();
                const text = btn.closest('.finding-item').querySelector('.finding-text').textContent;
                navigator.clipboard.writeText(text).then(() => {{
                    showToast('✓ Copied to clipboard');
                }}).catch(() => {{
                    // Fallback for older browsers
                    const ta = document.createElement('textarea');
                    ta.value = text;
                    ta.style.position = 'fixed';
                    ta.style.opacity = '0';
                    document.body.appendChild(ta);
                    ta.select();
                    document.execCommand('copy');
                    document.body.removeChild(ta);
                    showToast('✓ Copied to clipboard');
                }});
            }});
        }});

        // ============================================================
        // Global Search / Filter
        // ============================================================
        const searchInput = document.getElementById('searchInput');
        const searchClear = document.getElementById('searchClear');

        const performSearch = (query) => {{
            const q = query.trim().toLowerCase();
            searchClear.classList.toggle('visible', q.length > 0);

            document.querySelectorAll('.finding-item').forEach(item => {{
                const text = item.textContent.toLowerCase();
                item.style.display = (!q || text.includes(q)) ? '' : 'none';
            }});
        }};

        searchInput.addEventListener('input', (e) => performSearch(e.target.value));

        searchClear.addEventListener('click', () => {{
            searchInput.value = '';
            performSearch('');
            searchInput.focus();
        }});

        // ============================================================
        // Keyboard Shortcuts
        // ============================================================
        document.addEventListener('keydown', (e) => {{
            // Skip if typing in an input
            if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

            if (e.key === 't' || e.key === 'T') {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}

            const tabKeys = {{'1': 'overview', '2': 'network', '3': 'web', '4': 'services', '5': 'recommendations'}};
            if (tabKeys[e.key]) {{
                const button = document.querySelector(`[data-tab="${{tabKeys[e.key]}}"]`);
                if (button) button.click();
            }}

            // '/' to focus search
            if (e.key === '/') {{
                e.preventDefault();
                searchInput.focus();
                searchInput.select();
            }}
        }});

        console.log('%c Security Report Loaded ', 'background: #ff6b35; color: white; font-size: 16px; padding: 10px; font-weight: bold;');
        console.log('%c Keyboard Shortcuts: T = Top | 1-5 = Tabs | / = Search ', 'color: #00d4ff; font-size: 12px;');
    </script>
</body>
</html>'''

    return report_html

def _generate_donut_chart(stats: dict) -> str:
    """Generate an SVG donut chart showing vulnerability severity distribution"""
    total = stats['critical'] + stats['high'] + stats['medium'] + stats['low']
    if total == 0:
        return ''

    radius = 60
    circumference = 2 * 3.14159 * radius
    colors = {
        'critical': ('#ff3b3b', 'Critical', stats['critical']),
        'high':     ('#ff8c42', 'High',     stats['high']),
        'medium':   ('#ffd23f', 'Medium',   stats['medium']),
        'low':      ('#3bceac', 'Low',      stats['low']),
    }

    # Build SVG segments
    segments = ''
    offset = 0.0
    for key, (color, label, count) in colors.items():
        if count == 0:
            continue
        fraction = count / total
        dash = fraction * circumference
        gap = circumference - dash
        segments += (
            f'<circle cx="80" cy="80" r="{radius}" fill="none" stroke="{color}" '
            f'stroke-width="20" stroke-dasharray="{dash:.2f} {gap:.2f}" '
            f'stroke-dashoffset="{-offset:.2f}" style="transition: stroke-dasharray 0.6s ease;">'
            f'<title>{label}: {count} ({fraction*100:.1f}%)</title></circle>'
        )
        offset += dash

    # Legend items
    legend_items = ''
    for key, (color, label, count) in colors.items():
        pct = f'{count/total*100:.0f}%' if total > 0 else '0%'
        legend_items += (
            f'<div class="legend-item">'
            f'<span class="legend-dot" style="background:{color};" aria-hidden="true"></span>'
            f'<span class="legend-label">{label}</span>'
            f'<span class="legend-value">{count} <span style="color:var(--text-tertiary);font-weight:400;font-size:0.8rem;">({pct})</span></span>'
            f'</div>'
        )

    return f'''
        <div class="section" style="margin-top:24px;">
            <div class="section-header">
                <h2 class="section-title">
                    <span class="section-icon" aria-hidden="true">📊</span>
                    Vulnerability Distribution
                </h2>
            </div>
            <div class="donut-chart-container" role="img" aria-label="Donut chart: {stats['critical']} critical, {stats['high']} high, {stats['medium']} medium, {stats['low']} low">
                <svg width="160" height="160" viewBox="0 0 160 160" class="donut-svg" aria-hidden="true">
                    <circle cx="80" cy="80" r="{radius}" fill="none" stroke="var(--bg-tertiary)" stroke-width="20"/>
                    {segments}
                    <text x="80" y="85" text-anchor="middle"
                          style="fill:var(--text-primary);font-size:1.2rem;font-weight:800;font-family:Inter,sans-serif;"
                          transform="rotate(90,80,80)">{total}</text>
                    <text x="80" y="100" text-anchor="middle"
                          style="fill:var(--text-tertiary);font-size:0.55rem;font-family:Inter,sans-serif;"
                          transform="rotate(90,80,80)">TOTAL</text>
                </svg>
                <div class="donut-legend">
                    {legend_items}
                </div>
            </div>
        </div>'''


def _generate_findings(findings: list, empty_message: Optional[str] = None, severity_class: str = "") -> str:
    """Generate HTML for findings list with severity detection"""
    if not findings:
        return f'''
            <div class="empty-state">
                <div class="empty-state-icon">✓</div>
                <div class="empty-state-text">{empty_message or "No findings detected"}</div>
            </div>
        '''

    import html as _html
    result = ''
    for finding in findings:
        # Auto-detect severity from content
        detected_severity = severity_class
        finding_lower = finding.lower()

        if not detected_severity:
            if 'critical' in finding_lower or 'ms17-010' in finding_lower or 'eternalblue' in finding_lower:
                detected_severity = 'critical'
            elif 'high' in finding_lower or 'dangerous' in finding_lower:
                detected_severity = 'high'
            elif 'medium' in finding_lower or 'warning' in finding_lower:
                detected_severity = 'medium'

        # Escape HTML entities to prevent XSS and truncate if too long
        safe_finding = _html.escape(finding, quote=True)
        if len(safe_finding) > 500:
            safe_finding = safe_finding[:497] + '...'

        result += (
            f'<div class="finding-item {detected_severity}" role="listitem">'
            f'<div class="finding-header">'
            f'<pre class="finding-text">{safe_finding}</pre>'
            f'<button class="copy-btn" aria-label="Copy finding to clipboard">Copy</button>'
            f'</div>'
            f'</div>\n'
        )

    return result

def _generate_services_table(services: list, critical_services: list) -> str:
    """Generate HTML table for services"""
    if not services:
        return '''
            <div class="empty-state">
                <div class="empty-state-icon">🔍</div>
                <div class="empty-state-text">No services detected or scan not performed</div>
            </div>
        '''

    import html as _html
    critical_ports = ['445', '3389', '22', '21', '23', '1433', '3306', '5432']

    result = '<table class="services-table" role="table" aria-label="Detected services">'
    result += '<thead><tr><th scope="col">Service Information</th><th scope="col">Status</th></tr></thead>'
    result += '<tbody>'

    for service in services:
        is_critical = any(port in service for port in critical_ports)
        badge = '<span class="service-badge critical">CRITICAL</span>' if is_critical else ''
        safe_service = _html.escape(service, quote=True)
        result += f'<tr><td>{safe_service}</td><td>{badge}</td></tr>\n'

    result += '</tbody></table>'

    return result

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: html_generator.py <outdir> <target> <url> <domain> <scan_mode>")
        sys.exit(1)

    outdir = sys.argv[1]
    target = sys.argv[2]
    url = sys.argv[3] if sys.argv[3] != 'NONE' else ''
    domain = sys.argv[4] if sys.argv[4] != 'NONE' else ''
    scan_mode = sys.argv[5]

    try:
        html = generate_html_report(outdir, target, url, domain, scan_mode)

        # Write to file
        output_file = f'{outdir}/reports/assessment.html'
        Path(f'{outdir}/reports').mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"[SUCCESS] HTML Report: {output_file} ({len(html)} bytes)")
        print(f"[INFO] Open in browser: file://{Path(output_file).absolute()}")
    except Exception as e:
        print(f"[ERROR] Failed to generate HTML report: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)