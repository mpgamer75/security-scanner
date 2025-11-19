#!/usr/bin/env python3
"""
Security Scanner HTML Report Generator
Modern, professional HTML report generation with 2025 design standards
"""

import sys
import json
from datetime import datetime
from pathlib import Path

def generate_html_report(outdir, target, url, domain, scan_mode):
    """Generate a modern, professional HTML report"""

    # Read statistics from files
    stats = {
        'critical': 0,
        'high': 0,
        'medium': 0,
        'low': 0,
        'ports': 0,
        'subs': 0
    }

    # Count vulnerabilities
    files = {
        'nmap_vulns': f'{outdir}/network/nmap_vulns.txt',
        'nmap_critical': f'{outdir}/network/nmap_critical_vulns.txt',
        'nuclei': f'{outdir}/web/nuclei.txt',
        'nmap_ports': f'{outdir}/network/nmap_ports.txt',
        'subdomains': f'{outdir}/osint/all_subdomains.txt'
    }

    for key, filepath in files.items():
        try:
            with open(filepath, 'r') as f:
                content = f.read()
                if key == 'nmap_vulns':
                    stats['critical'] += content.lower().count('vulnerable')
                elif key == 'nmap_critical':
                    stats['high'] += content.lower().count('critical')
                    stats['high'] += content.lower().count('ms17-010')
                elif key == 'nuclei':
                    stats['medium'] += content.lower().count('medium')
                elif key == 'nmap_ports':
                    stats['ports'] = content.count('open')
                elif key == 'subdomains':
                    stats['subs'] = len([l for l in content.splitlines() if l.strip()])
        except FileNotFoundError:
            continue

    # Calculate risk score
    risk_score = min(100, stats['critical'] * 10 + stats['high'] * 5 + stats['medium'] * 2)

    if risk_score >= 70:
        risk_level = "CRITICAL"
        risk_color = "#dc3545"
    elif risk_score >= 40:
        risk_level = "HIGH"
        risk_color = "#fd7e14"
    elif risk_score >= 20:
        risk_level = "MEDIUM"
        risk_color = "#ffc107"
    else:
        risk_level = "LOW"
        risk_color = "#28a745"

    # Read findings
    network_vulns = []
    web_vulns = []
    services = []

    try:
        with open(f'{outdir}/network/nmap_vulns.txt', 'r') as f:
            for line in f:
                if 'VULNERABLE' in line.upper():
                    network_vulns.append(line.strip())
                    if len(network_vulns) >= 20:
                        break
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/web/nuclei.txt', 'r') as f:
            web_vulns = [line.strip() for line in f if line.strip()][:20]
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/network/nmap_services.txt', 'r') as f:
            for line in f:
                if 'open' in line.lower():
                    services.append(line.strip())
                    if len(services) >= 20:
                        break
    except FileNotFoundError:
        pass

    # Generate HTML
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Security Assessment Report - {target}</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e27;
            --bg-secondary: #0f1729;
            --bg-card: rgba(15, 23, 42, 0.8);
            --bg-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --accent-primary: #ef4444;
            --accent-secondary: #3b82f6;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, #1a1f3a 50%, var(--bg-secondary) 100%);
            background-attachment: fixed;
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
        }}

        .glass-card {{
            background: var(--bg-glass);
            backdrop-filter: blur(20px);
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.3) 100%);
            border-bottom: 1px solid rgba(239, 68, 68, 0.3);
            padding: 60px 40px;
            text-align: center;
        }}

        .header h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 800;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #fff 0%, #ef4444 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -1px;
        }}

        .header .subtitle {{
            font-size: 1.25rem;
            font-weight: 500;
            color: var(--text-secondary);
            letter-spacing: 2px;
            text-transform: uppercase;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 20px;
            padding: 40px;
        }}

        .info-card {{
            background: var(--bg-glass);
            backdrop-filter: blur(10px);
            padding: 24px;
            border-radius: 16px;
            border: 1px solid var(--border-glass);
            transition: all 0.3s ease;
        }}

        .info-card:hover {{
            transform: translateY(-4px);
            border-color: rgba(59, 130, 246, 0.3);
            box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
        }}

        .info-card h3 {{
            color: var(--accent-secondary);
            margin-bottom: 12px;
            font-size: 0.85rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }}

        .info-card p {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
            gap: 24px;
            padding: 40px;
        }}

        .stat-card {{
            background: var(--bg-glass);
            backdrop-filter: blur(10px);
            padding: 32px 24px;
            border-radius: 20px;
            text-align: center;
            border: 1px solid var(--border-glass);
            transition: all 0.4s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        }}

        .stat-card .number {{
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 12px;
            line-height: 1;
        }}

        .stat-card .label {{
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
        }}

        .stat-card.critical .number {{ color: #ef4444; }}
        .stat-card.high .number {{ color: #f59e0b; }}
        .stat-card.medium .number {{ color: #f59e0b; }}
        .stat-card.info .number {{ color: #3b82f6; }}

        .section {{
            padding: 40px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }}

        .section h2 {{
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 28px;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            gap: 12px;
        }}

        .section h2::before {{
            content: '';
            width: 4px;
            height: 32px;
            background: linear-gradient(180deg, var(--accent-primary), transparent);
            border-radius: 2px;
        }}

        .risk-badge {{
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 24px;
            border-radius: 12px;
            font-weight: 600;
            font-size: 1.1rem;
            margin: 16px 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        }}

        .accordion {{
            background: var(--bg-glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            margin: 20px 0;
            overflow: hidden;
        }}

        .accordion-header {{
            padding: 20px 24px;
            cursor: pointer;
            font-weight: 600;
            font-size: 1.1rem;
            color: var(--accent-secondary);
            display: flex;
            justify-content: space-between;
            align-items: center;
            transition: all 0.3s ease;
        }}

        .accordion-header:hover {{
            background: rgba(59, 130, 246, 0.05);
        }}

        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s ease;
        }}

        .accordion.active .accordion-content {{
            max-height: 2000px;
        }}

        .findings-list {{
            padding: 24px;
            background: rgba(0, 0, 0, 0.2);
        }}

        .finding-item {{
            background: var(--bg-glass);
            padding: 16px 20px;
            margin: 12px 0;
            border-left: 3px solid var(--accent-primary);
            border-radius: 8px;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }}

        .finding-item:hover {{
            background: rgba(239, 68, 68, 0.05);
            transform: translateX(4px);
        }}

        .code-block {{
            background: #0d1117;
            border: 1px solid #30363d;
            border-radius: 12px;
            padding: 20px;
            margin: 16px 0;
            overflow-x: auto;
            font-family: 'JetBrains Mono', monospace;
            font-size: 0.9rem;
        }}

        .recommendation {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
            border-left: 3px solid var(--accent-secondary);
            padding: 20px;
            margin: 16px 0;
            border-radius: 12px;
        }}

        .recommendation strong {{
            color: var(--accent-secondary);
            display: block;
            margin-bottom: 8px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 24px 0;
            background: var(--bg-glass);
            border-radius: 12px;
            overflow: hidden;
        }}

        th, td {{
            padding: 16px 20px;
            text-align: left;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
        }}

        th {{
            background: rgba(239, 68, 68, 0.2);
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            color: var(--accent-primary);
        }}

        tr:hover {{
            background: rgba(59, 130, 246, 0.05);
        }}

        .footer {{
            padding: 40px;
            text-align: center;
            border-top: 1px solid rgba(239, 68, 68, 0.2);
            margin-top: 40px;
            color: var(--text-secondary);
        }}

        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .info-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="glass-card">
            <div class="header">
                <h1>SECURITY ASSESSMENT</h1>
                <div class="subtitle">Red Team Penetration Testing Report</div>
            </div>

            <div class="info-grid">
                <div class="info-card">
                    <h3>Target</h3>
                    <p>{target}</p>
                </div>
                {f'<div class="info-card"><h3>URL</h3><p>{url}</p></div>' if url else ''}
                {f'<div class="info-card"><h3>Domain</h3><p>{domain}</p></div>' if domain else ''}
                <div class="info-card">
                    <h3>Assessment Date</h3>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                <div class="info-card">
                    <h3>Scanner Version</h3>
                    <p>v2.3.3</p>
                </div>
                <div class="info-card">
                    <h3>Scan Mode</h3>
                    <p>{scan_mode}</p>
                </div>
            </div>

            <div class="stats-grid">
                <div class="stat-card critical">
                    <div class="number">{stats['critical']}</div>
                    <div class="label">Critical Vulnerabilities</div>
                </div>
                <div class="stat-card high">
                    <div class="number">{stats['high']}</div>
                    <div class="label">High Risk Issues</div>
                </div>
                <div class="stat-card medium">
                    <div class="number">{stats['medium']}</div>
                    <div class="label">Medium Risk Issues</div>
                </div>
                <div class="stat-card info">
                    <div class="number">{stats['ports']}</div>
                    <div class="label">Open Ports</div>
                </div>
                <div class="stat-card info">
                    <div class="number">{stats['subs']}</div>
                    <div class="label">Subdomains Found</div>
                </div>
            </div>

            <div class="section">
                <h2>Risk Assessment</h2>
                <p><strong>Risk Score:</strong> {risk_score}/100</p>
                <div class="risk-badge" style="background-color: {risk_color};">
                    Risk Level: {risk_level}
                </div>
            </div>

            <div class="section">
                <h2>Network Vulnerabilities</h2>
                <div class="accordion active" onclick="this.classList.toggle('active')">
                    <div class="accordion-header">
                        View Network Findings
                        <span>▼</span>
                    </div>
                    <div class="accordion-content">
                        <div class="findings-list">
                            {_generate_findings(network_vulns, "No network vulnerabilities detected or scan not performed")}
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Web Application Vulnerabilities</h2>
                <div class="accordion active" onclick="this.classList.toggle('active')">
                    <div class="accordion-header">
                        View Web Findings
                        <span>▼</span>
                    </div>
                    <div class="accordion-content">
                        <div class="findings-list">
                            {_generate_findings(web_vulns, "No web vulnerabilities detected or scan not performed")}
                        </div>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Open Services</h2>
                <div class="accordion active" onclick="this.classList.toggle('active')">
                    <div class="accordion-header">
                        View Detected Services
                        <span>▼</span>
                    </div>
                    <div class="accordion-content">
                        <table>
                            <thead>
                                <tr><th>Service Information</th></tr>
                            </thead>
                            <tbody>
                                {_generate_services(services)}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Recommendations</h2>
                <h3>Immediate Actions:</h3>
                <div class="recommendation">
                    <strong>1. Patch Critical Vulnerabilities</strong>
                    <p>Address all identified critical vulnerabilities immediately to reduce attack surface.</p>
                </div>
                <div class="recommendation">
                    <strong>2. Disable Unnecessary Services</strong>
                    <p>Review and disable any services that are not essential for business operations.</p>
                </div>
                <div class="recommendation">
                    <strong>3. Implement Strong Authentication</strong>
                    <p>Enforce multi-factor authentication (MFA) for all critical systems and services.</p>
                </div>
                <div class="recommendation">
                    <strong>4. Deploy Network Segmentation</strong>
                    <p>Implement proper network segmentation to limit lateral movement in case of breach.</p>
                </div>
                <div class="recommendation">
                    <strong>5. Enable Comprehensive Logging</strong>
                    <p>Ensure all systems have proper logging enabled for incident detection and response.</p>
                </div>

                <h3 style="margin-top: 32px;">Red Team Next Steps:</h3>
                <div class="code-block">
# Review exploit scripts
cd exploit/

# Test default credentials
cat credentials.txt

# Run automated attacks (with authorization)
./auto_attack.sh

# Execute Metasploit modules
cat msf_prep.txt
                </div>
            </div>

            <div class="footer">
                <p><strong>Security Scanner v2.3.3</strong></p>
                <p>Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p style="margin-top: 10px;">This tool is for authorized security testing only. Unauthorized use is illegal.</p>
            </div>
        </div>
    </div>
</body>
</html>'''

    return html

def _generate_findings(findings, empty_message):
    """Generate HTML for findings list"""
    if not findings:
        return f'<p>{empty_message}</p>'

    html = ''
    for finding in findings:
        html += f'<div class="finding-item"><p>{finding}</p></div>\n'
    return html

def _generate_services(services):
    """Generate HTML for services table"""
    if not services:
        return '<tr><td>No services detected or scan not performed</td></tr>'

    html = ''
    for service in services:
        html += f'<tr><td>{service}</td></tr>\n'
    return html

if __name__ == '__main__':
    if len(sys.argv) < 6:
        print("Usage: html_generator.py <outdir> <target> <url> <domain> <scan_mode>")
        sys.exit(1)

    outdir = sys.argv[1]
    target = sys.argv[2]
    url = sys.argv[3] if sys.argv[3] != 'NONE' else ''
    domain = sys.argv[4] if sys.argv[4] != 'NONE' else ''
    scan_mode = sys.argv[5]

    html = generate_html_report(outdir, target, url, domain, scan_mode)

    # Write to file
    output_file = f'{outdir}/reports/assessment.html'
    with open(output_file, 'w') as f:
        f.write(html)

    print(f"[SUCCESS] HTML Report: {output_file} ({len(html)} bytes)")
    print(f"[INFO] Open in browser: file://{Path(output_file).absolute()}")
