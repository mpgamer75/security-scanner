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
    """Generate a modern, professional HTML report with enhanced CSS and JavaScript"""

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
                    stats['high'] += content.lower().count('[high]')
                    stats['critical'] += content.lower().count('[critical]')
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
                    if len(network_vulns) >= 50:
                        break
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/web/nuclei.txt', 'r') as f:
            web_vulns = [line.strip() for line in f if line.strip()][:50]
    except FileNotFoundError:
        pass

    try:
        with open(f'{outdir}/network/nmap_services.txt', 'r') as f:
            for line in f:
                if 'open' in line.lower():
                    services.append(line.strip())
                    if len(services) >= 30:
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
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-primary: #0a0e27;
            --bg-secondary: #0f1729;
            --bg-tertiary: #1a1f3a;
            --bg-card: rgba(15, 23, 42, 0.8);
            --bg-glass: rgba(255, 255, 255, 0.05);
            --border-glass: rgba(255, 255, 255, 0.1);
            --accent-primary: #ef4444;
            --accent-secondary: #3b82f6;
            --accent-success: #10b981;
            --accent-warning: #f59e0b;
            --text-primary: #f1f5f9;
            --text-secondary: #94a3b8;
            --text-dim: #64748b;
            --shadow-glow-red: 0 0 30px rgba(239, 68, 68, 0.3);
            --shadow-glow-blue: 0 0 30px rgba(59, 130, 246, 0.3);
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-tertiary) 50%, var(--bg-secondary) 100%);
            background-attachment: fixed;
            color: var(--text-primary);
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
            animation: fadeIn 0.6s ease-in;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; }}
            to {{ opacity: 1; }}
        }}

        @keyframes slideUp {{
            from {{
                opacity: 0;
                transform: translateY(30px);
            }}
            to {{
                opacity: 1;
                transform: translateY(0);
            }}
        }}

        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}

        @keyframes shimmer {{
            0% {{ background-position: -1000px 0; }}
            100% {{ background-position: 1000px 0; }}
        }}

        .container {{
            max-width: 1600px;
            margin: 0 auto;
            animation: slideUp 0.8s ease-out;
        }}

        .glass-card {{
            background: var(--bg-glass);
            backdrop-filter: blur(20px) saturate(180%);
            -webkit-backdrop-filter: blur(20px) saturate(180%);
            border: 1px solid var(--border-glass);
            border-radius: 24px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4),
                        0 0 0 1px rgba(255, 255, 255, 0.05) inset;
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .glass-card:hover {{
            box-shadow: 0 12px 48px rgba(0, 0, 0, 0.5),
                        0 0 0 1px rgba(255, 255, 255, 0.08) inset;
        }}

        .header {{
            background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(220, 38, 38, 0.3) 100%);
            border-bottom: 1px solid rgba(239, 68, 68, 0.3);
            padding: 60px 40px;
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
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.03), transparent);
            animation: shimmer 3s infinite;
        }}

        .header h1 {{
            font-size: clamp(2rem, 5vw, 3.5rem);
            font-weight: 900;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #fff 0%, #ef4444 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            letter-spacing: -2px;
            position: relative;
            z-index: 1;
        }}

        .header .subtitle {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-secondary);
            letter-spacing: 3px;
            text-transform: uppercase;
            position: relative;
            z-index: 1;
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
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
        }}

        .info-card:hover {{
            transform: translateY(-4px) scale(1.02);
            border-color: rgba(59, 130, 246, 0.4);
            box-shadow: 0 8px 25px rgba(59, 130, 246, 0.2);
        }}

        .info-card h3 {{
            color: var(--accent-secondary);
            margin-bottom: 12px;
            font-size: 0.85rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }}

        .info-card p {{
            font-size: 1.25rem;
            font-weight: 600;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', monospace;
            word-break: break-all;
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
            transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
            cursor: default;
            position: relative;
            overflow: hidden;
        }}

        .stat-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, transparent, currentColor, transparent);
            opacity: 0;
            transition: opacity 0.3s ease;
        }}

        .stat-card:hover {{
            transform: translateY(-8px);
            box-shadow: 0 12px 40px rgba(0, 0, 0, 0.5);
        }}

        .stat-card:hover::before {{
            opacity: 1;
        }}

        .stat-card .number {{
            font-size: 4rem;
            font-weight: 800;
            margin-bottom: 12px;
            line-height: 1;
            transition: transform 0.3s ease;
        }}

        .stat-card:hover .number {{
            transform: scale(1.1);
        }}

        .stat-card .label {{
            font-size: 0.9rem;
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            color: var(--text-secondary);
        }}

        .stat-card.critical {{ color: #ef4444; }}
        .stat-card.critical .number {{ color: #ef4444; text-shadow: 0 0 20px rgba(239, 68, 68, 0.5); }}
        .stat-card.high {{ color: #f59e0b; }}
        .stat-card.high .number {{ color: #f59e0b; text-shadow: 0 0 20px rgba(245, 158, 11, 0.5); }}
        .stat-card.medium {{ color: #f59e0b; }}
        .stat-card.medium .number {{ color: #f59e0b; }}
        .stat-card.info {{ color: #3b82f6; }}
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

        .section h3 {{
            font-size: 1.5rem;
            font-weight: 600;
            margin: 32px 0 16px 0;
            color: var(--accent-secondary);
        }}

        .risk-badge {{
            display: inline-flex;
            align-items: center;
            gap: 12px;
            padding: 16px 32px;
            border-radius: 12px;
            font-weight: 700;
            font-size: 1.2rem;
            margin: 16px 0;
            box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
            transition: all 0.3s ease;
            cursor: default;
        }}

        .risk-badge:hover {{
            transform: scale(1.05);
            box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
        }}

        .risk-badge::before {{
            content: '⚠';
            font-size: 1.5rem;
        }}

        .accordion {{
            background: var(--bg-glass);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border-glass);
            border-radius: 16px;
            margin: 20px 0;
            overflow: hidden;
            transition: all 0.3s ease;
        }}

        .accordion:hover {{
            border-color: rgba(59, 130, 246, 0.3);
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
            user-select: none;
        }}

        .accordion-header:hover {{
            background: rgba(59, 130, 246, 0.05);
        }}

        .accordion-header:active {{
            background: rgba(59, 130, 246, 0.1);
        }}

        .accordion-arrow {{
            transition: transform 0.3s ease;
            font-size: 1.2rem;
        }}

        .accordion.active .accordion-arrow {{
            transform: rotate(180deg);
        }}

        .accordion-content {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        }}

        .accordion.active .accordion-content {{
            max-height: 3000px;
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
            cursor: default;
        }}

        .finding-item:hover {{
            background: rgba(239, 68, 68, 0.1);
            transform: translateX(8px);
            border-left-width: 5px;
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
            transition: all 0.3s ease;
        }}

        .code-block:hover {{
            border-color: #58a6ff;
            box-shadow: 0 0 0 1px #58a6ff;
        }}

        .recommendation {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.1), rgba(59, 130, 246, 0.05));
            border-left: 3px solid var(--accent-secondary);
            padding: 20px;
            margin: 16px 0;
            border-radius: 12px;
            transition: all 0.3s ease;
        }}

        .recommendation:hover {{
            background: linear-gradient(135deg, rgba(59, 130, 246, 0.15), rgba(59, 130, 246, 0.08));
            transform: translateX(4px);
        }}

        .recommendation strong {{
            color: var(--accent-secondary);
            display: block;
            margin-bottom: 8px;
            font-size: 1.1rem;
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
            letter-spacing: 1px;
        }}

        tr {{
            transition: background 0.2s ease;
        }}

        tr:hover {{
            background: rgba(59, 130, 246, 0.05);
        }}

        tbody tr:last-child td {{
            border-bottom: none;
        }}

        .footer {{
            padding: 40px;
            text-align: center;
            border-top: 1px solid rgba(239, 68, 68, 0.2);
            margin-top: 40px;
            color: var(--text-secondary);
        }}

        .footer p {{
            margin: 8px 0;
        }}

        .scroll-top {{
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 50px;
            height: 50px;
            background: var(--accent-primary);
            color: white;
            border: none;
            border-radius: 50%;
            cursor: pointer;
            display: none;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
            transition: all 0.3s ease;
            z-index: 1000;
        }}

        .scroll-top:hover {{
            background: #dc2626;
            transform: translateY(-5px);
            box-shadow: 0 8px 20px rgba(239, 68, 68, 0.6);
        }}

        .scroll-top.visible {{
            display: flex;
        }}

        @media (max-width: 768px) {{
            .stats-grid {{ grid-template-columns: repeat(2, 1fr); }}
            .info-grid {{ grid-template-columns: 1fr; }}
            .header {{ padding: 40px 20px; }}
            .section {{ padding: 20px; }}
            .stat-card .number {{ font-size: 3rem; }}
        }}

        /* Print styles */
        @media print {{
            body {{
                background: white;
                color: black;
            }}
            .glass-card {{
                box-shadow: none;
                border: 1px solid #ccc;
            }}
            .scroll-top {{
                display: none !important;
            }}
            .accordion-content {{
                max-height: none !important;
            }}
        }}
    </style>
</head>
<body>
    <button class="scroll-top" id="scrollTop" aria-label="Scroll to top">↑</button>

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
                {f'<div class="info-card"><h3>URL</h3><p>{url}</p></div>' if url and url != 'NONE' else ''}
                {f'<div class="info-card"><h3>Domain</h3><p>{domain}</p></div>' if domain and domain != 'NONE' else ''}
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
                <div class="accordion active" data-accordion="network">
                    <div class="accordion-header">
                        <span>View Network Findings ({len(network_vulns)} issues)</span>
                        <span class="accordion-arrow">▼</span>
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
                <div class="accordion active" data-accordion="web">
                    <div class="accordion-header">
                        <span>View Web Findings ({len(web_vulns)} issues)</span>
                        <span class="accordion-arrow">▼</span>
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
                <div class="accordion active" data-accordion="services">
                    <div class="accordion-header">
                        <span>View Detected Services ({len(services)} services)</span>
                        <span class="accordion-arrow">▼</span>
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

    <script>
        // Accordion functionality
        document.querySelectorAll('.accordion').forEach(accordion => {{
            const header = accordion.querySelector('.accordion-header');
            header.addEventListener('click', () => {{
                accordion.classList.toggle('active');
            }});
        }});

        // Scroll to top button
        const scrollTopBtn = document.getElementById('scrollTop');

        window.addEventListener('scroll', () => {{
            if (window.pageYOffset > 300) {{
                scrollTopBtn.classList.add('visible');
            }} else {{
                scrollTopBtn.classList.remove('visible');
            }}
        }});

        scrollTopBtn.addEventListener('click', () => {{
            window.scrollTo({{
                top: 0,
                behavior: 'smooth'
            }});
        }});

        // Animate stats on scroll
        const animateStats = () => {{
            const statCards = document.querySelectorAll('.stat-card .number');
            const observer = new IntersectionObserver((entries) => {{
                entries.forEach(entry => {{
                    if (entry.isIntersecting) {{
                        const target = parseInt(entry.target.textContent);
                        animateNumber(entry.target, target);
                        observer.unobserve(entry.target);
                    }}
                }});
            }}, {{ threshold: 0.5 }});

            statCards.forEach(card => observer.observe(card));
        }};

        const animateNumber = (element, target) => {{
            let current = 0;
            const increment = target / 50;
            const timer = setInterval(() => {{
                current += increment;
                if (current >= target) {{
                    element.textContent = target;
                    clearInterval(timer);
                }} else {{
                    element.textContent = Math.floor(current);
                }}
            }}, 20);
        }};

        // Initialize animations
        if ('IntersectionObserver' in window) {{
            animateStats();
        }}

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {{
            // Press 'T' to scroll to top
            if (e.key === 't' || e.key === 'T') {{
                window.scrollTo({{ top: 0, behavior: 'smooth' }});
            }}
            // Press 'E' to expand/collapse all accordions
            if (e.key === 'e' || e.key === 'E') {{
                document.querySelectorAll('.accordion').forEach(acc => {{
                    acc.classList.toggle('active');
                }});
            }}
        }});

        // Add tooltips for stats
        document.querySelectorAll('.stat-card').forEach(card => {{
            card.setAttribute('title', 'Click to highlight related findings');
        }});

        console.log('%c Security Assessment Report Loaded ', 'background: #ef4444; color: white; font-size: 16px; padding: 10px;');
        console.log('%c Keyboard Shortcuts: T = Scroll to top | E = Expand/Collapse all ', 'color: #3b82f6; font-size: 12px;');
    </script>
</body>
</html>'''

    return html

def _generate_findings(findings, empty_message):
    """Generate HTML for findings list"""
    if not findings:
        return f'<p style="color: var(--text-secondary); font-style: italic;">{empty_message}</p>'

    html = ''
    for finding in findings:
        html += f'<div class="finding-item"><p>{finding}</p></div>\n'
    return html

def _generate_services(services):
    """Generate HTML for services table"""
    if not services:
        return '<tr><td style="color: var(--text-secondary); font-style: italic;">No services detected or scan not performed</td></tr>'

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
