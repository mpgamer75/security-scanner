<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.4.0-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

**Security Scanner v2.4.0**: Advanced red team assessment tool. Designed for professional penetration testers and security researchers.

## What's New in v2.4.0

### Modular Architecture

- **Modularized codebase** - Split monolithic 1,868-line script into 5 sourced modules
  - `security` (874 lines): Core framework, report generation, main()
  - `lib/osint.sh` (192 lines): WHOIS, DNS, subdomains, crt.sh
  - `lib/network.sh` (217 lines): Port scanning, service detection
  - `lib/web.sh` (229 lines): Tech fingerprinting, WAF, SSL, directory enumeration, vulnerability scanning
  - `lib/exploit.sh` (415 lines): Searchsploit, Metasploit prep, credentials, post-exploitation
- **Flexible module loading** - Searches `$SCRIPT_DIR/lib/`, `/usr/local/lib/`, `~/.local/lib/`

### Security Hardening

- **XSS prevention** - HTML reports use `html.escape()` for all user-controlled data
- **Input validation** - New `validate_ip()`, `validate_domain()`, `validate_url()`, `validate_target()` functions
- **Secure file permissions** - `umask 077` for owner-only access on scan output directories
- **JSON injection prevention** - New `json_escape()` function for safe JSON output
- **Structured logging** - Timestamped entries in `reports/scanner.log`

### Next-Gen HTML Reports

- **Light/dark mode** - Toggle with `prefers-color-scheme` support and localStorage persistence
- **Scroll progress bar** - Visual indicator at top of page
- **Accessibility** - Skip-nav link, ARIA roles, visible focus outlines, aria-hidden on decorative icons
- **Global search** - Filter all findings with `/` keyboard shortcut
- **Severity filters** - Buttons (All/Critical/High/Medium) per section
- **Copy-to-clipboard** - Per-finding button with toast notification
- **SVG donut chart** - Vulnerability severity distribution visualization

### CI/CD, Docker & Testing

- **GitHub Actions CI** - ShellCheck, pylint, smoke tests, XSS verification, Bandit security scan
- **32 unit tests** - `tests/test_html_generator.py` (all passing)
- **ShellCheck clean** - All scripts pass shellcheck
- **Docker** - Kali Linux Dockerfile + docker-compose.yml with output volume
- **Configuration** - Template `config.yml.example` with timeouts, wordlists, API keys

## What's New in v2.3.4

### Critical Fixes and Major Improvements

- **Fixed scan timeouts** - Aligned bash/nmap timeouts to prevent interruptions
- **Improved vulnerability detection** - Complete scans even on slow targets
- **Fixed HTML report display** - "Critical Services Detected" section now displays correctly
- **Intelligent Network filtering** - Excludes scan messages, shows only real vulnerabilities
- **Optimized timeouts** - TIMEOUT_LONG increased to 900s (15 min) aligned with nmap
- **Fixed Quick mode** - Dynamic timeouts based on selected mode

## What's New in v2.3.3

### Major Optimizations and New Features

- **HTML report generation** - Modern interactive visual reports with professional CSS
- **Parallelized scans** - Parallel subdomain enumeration (subfinder, assetfinder, findomain)
- **Further optimized Nmap scans** - Extended coverage with --top-ports 3000, min-rate 3000
- **Dynamic timeouts** - Adaptive timeouts based on mode (quick/stealth/aggressive)
- **Improved performance** - Up to 30% faster thanks to parallelization

## Installation

### Automatic Installation (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

This single command will:
- Download the script
- Install all dependencies
- Configure the tool in /usr/local/bin
- Make the `security` command globally available

### Docker Installation

```bash
# Clone the repository
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner

# Launch with Docker Compose
docker-compose up -d

# Run a scan
docker exec -it security-scanner security
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner

# Run the installation script
chmod +x install.sh
./install.sh
```

The installer automatically detects your distribution and installs appropriate packages.

## Quick Start

### Basic Scan

```bash
security
# Enter target IP, URL, domain
# Select scan type (1-4)
```

### Quick Reconnaissance

```bash
security -q
# 3x faster, perfect for initial assessment
```

### Complete Red Team Assessment

```bash
security -a
# Full coverage: all ports, all tests, exploitation prep
```

### Stealth Mode

```bash
security -s
# IDS/IPS evasion, slower but stealthy
```

## Performance Comparison

| Operation | v2.2.1 | v2.3.3 | v2.3.4 | v2.4.0 | Improvement |
|-----------|--------|--------|--------|--------|-------------|
| Full assessment | approx. 60 min | approx. 14 min | approx. 14 min | approx. 12 min | **80% faster** |
| Port scanning | 10 min | 4 min | 4 min | 4 min | **60% faster** |
| Service detection | 20 min | 4 min | 4 min | 4 min | **80% faster** |
| Web scanning | 15 min | 4 min | 4 min | 4 min | **73% faster** |
| OSINT/Subdomains | 10 min | 3 min | 3 min | 3 min | **70% faster** |
| Report generation | 75% success | 100% success | 100% success | 100% success | **+25%** |
| Scan reliability | 85% | 95% | 100% | 100% | **+15%** |
| Vuln detection | Variable | Good | Excellent | Excellent | **No false negatives** |

## Prerequisites

### Core Tools (Auto-installed)

```bash
# Network tools
nmap masscan

# Web tools
gobuster nikto whatweb sqlmap

# OSINT tools
whois subfinder theHarvester

# Vulnerability scanners
nuclei
```

### Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap masscan gobuster sqlmap whois nikto whatweb

# Go tools (pinned versions)
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@v2.6.6
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@v3.2.4

# Python tools
pip3 install theHarvester
```

## Main Features

### 1. OSINT & Information Gathering

- **Fast subdomain enumeration** (Subfinder, Assetfinder, Findomain)
- **Email harvesting** (theHarvester)
- **Certificate transparency** (crt.sh)
- **DNS enumeration** (dig)
- **Google dorking** (automated queries)
- **Social media recon**

### 2. Network Reconnaissance

- **Optimized port scanning** (-Pn forced, smart timeouts)
- **Service detection** (Nmap NSE scripts)
- **OS fingerprinting**
- **Vulnerability detection** (vuln scripts)
- **SMB enumeration** (enum4linux, smbclient)
- **SNMP enumeration**

### 3. Web Application Testing

- **Technology fingerprinting** (WhatWeb, Wappalyzer)
- **WAF detection** (wafw00f)
- **Directory enumeration** (Gobuster)
- **Vulnerability scanning** (Nuclei, Nikto)
- **SSL/TLS analysis**
- **SQL injection testing** (SQLMap)

### 4. Exploitation Preparation

- **Exploit database search** (searchsploit)
- **Metasploit module prep**
- **Attack surface analysis**
- **Credential lists** (default passwords)
- **Automated attack scripts**
- **Post-exploitation checklist**

## Results Structure

```
redteam_20260322_143022/
├── osint/
│   ├── whois.txt
│   ├── dns.txt
│   ├── subdomains_subfinder.txt
│   ├── all_subdomains.txt          # Consolidated
│   ├── emails.txt
│   ├── crt_sh.txt
│   └── google_dorks.txt
├── network/
│   ├── nmap_ports.txt              # Port scan
│   ├── nmap_services.txt           # Service detection
│   ├── nmap_vulns.txt              # Vulnerabilities
│   ├── nmap_os.txt                 # OS detection
│   ├── smb_enum.txt                # SMB enumeration
│   └── snmp_enum.txt
├── web/
│   ├── whatweb.txt
│   ├── wafw00f.txt
│   ├── ssl_analysis.txt
│   ├── gobuster.txt
│   ├── nuclei.txt
│   └── nikto.txt
├── exploit/
│   ├── searchsploit.txt
│   ├── attack_surface.txt
│   ├── auto_attack.sh
│   └── credentials.txt
└── reports/
    ├── summary_report.txt          # Human-readable
    ├── assessment.json             # Machine-readable
    ├── assessment.html             # Interactive HTML report
    └── scanner.log                 # Timestamped log
```

## Usage Examples

### Example 1: Complete Web Assessment

```bash
security

Target IP: 192.168.1.100
Target URL: https://example.com
Domain: example.com

Select: [4] Complete Red Team Assessment

Results in: redteam_20260322_143022/
```

### Example 2: Quick Network Scan

```bash
security -q

Target IP: 10.0.0.50
Select: [2] Network Reconnaissance

# 3x faster than standard mode
```

### Example 3: Stealth OSINT

```bash
security -s

Target IP: 203.0.113.10
Domain: target.com
Select: [1] OSINT & Information Gathering

# Slow and stealthy, avoids detection
```

### Example 4: Docker Scan

```bash
docker-compose run --rm scanner security -a

# Isolated environment with all tools pre-installed
```

## Advanced Configuration

### Custom Timeouts

Edit `/usr/local/bin/security`:

```bash
# Line approximately 43-47 (v2.4.0 - Optimized and exported)
export TIMEOUT_VERY_SHORT=15
export TIMEOUT_SHORT=30
export TIMEOUT_MEDIUM=120
export TIMEOUT_LONG=900        # 15 min - aligned with nmap --host-timeout 15m
export TIMEOUT_VERY_LONG=1200  # 20 min - for complex vulnerability scans
```

### YAML Configuration (New)

```bash
cp config.yml.example config.yml
# Edit config.yml with your preferences:
# - Custom timeouts
# - Wordlist paths
# - API keys (Shodan, etc.)
# - Scan profiles
```

### Custom Wordlists

```bash
# Use your own wordlist
export CUSTOM_WORDLIST="/path/to/wordlist.txt"
gobuster dir -u $URL -w $CUSTOM_WORDLIST
```

## Anti-Blocking Features

### 1. Forced -Pn (No Ping)

All Nmap scans use `-Pn` to avoid blocking on non-pingable hosts:

```bash
nmap -Pn -sS $target  # Always works, never blocks
```

### 2. Smart Timeouts

```bash
--host-timeout 5m     # Max 5min per host
--max-retries 1       # Only 1 retry
--min-rate 2000       # Minimum 2000 packets/sec
```

### 3. Rate Limiting Bypass

```bash
--defeat-rst-ratelimit  # Bypass RST rate limiting
```

### 4. Fallback Mechanisms

If a tool fails, the scan continues with alternative tools or methods.

## Security Best Practices

### Legal Usage

- **Only test your own systems**
- **Get written authorization** before testing
- **Respect scope and rules of engagement**
- **Never test without permission**

### Operational Security

```bash
# Use VPN
openvpn --config vpn.conf

# Check your IP
curl ifconfig.me

# Use proxychains (optional)
proxychains security
```

### Responsible Disclosure

If you find vulnerabilities:

1. Document everything
2. Contact the vendor/organization
3. Give reasonable time to patch (90 days)
4. Disclose responsibly

## Troubleshooting

### Scans Too Slow?

```bash
# Use quick mode
security -q

# Or reduce timeouts
sudo nano /usr/local/bin/security
# Edit TIMEOUT_* variables
```

### Scans Block/Hang?

```bash
# Verify -Pn is present
grep "nmap -Pn" /usr/local/bin/security

# Update to latest version
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o /tmp/security_new
sudo mv /tmp/security_new /usr/local/bin/security
sudo chmod +x /usr/local/bin/security
```

### Reports Not Generated?

```bash
# Check individual files
find redteam_* -name "*.txt" -size +0

# Verify permissions
ls -la redteam_*/reports/

# Check the log
cat redteam_*/reports/scanner.log
```

### Tool Not Found?

```bash
# Install missing tools
sudo apt install nmap gobuster nikto

# Check installation
which nmap subfinder nuclei

# Reinstall if needed
./install.sh
```

## Roadmap

### Version 2.5.0 (Planned)

- Machine learning vulnerability correlation
- Web dashboard (real-time monitoring)
- PDF export with charts
- Direct Metasploit integration
- GNU Parallel support (parallelized network scans)

### Version 3.0.0 (Future)

- Distributed scanning (multi-host)
- REST API for automation
- Advanced CI/CD pipeline integration
- Cloud-native deployment

## Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Test on Ubuntu 22.04 and Kali Linux
- Follow bash best practices (ShellCheck clean)
- Document new features
- Keep backwards compatibility
- Add unit tests

## License

MIT License - see [LICENSE](LICENSE) file

## Author

**mpgamer75**

- GitHub: [@mpgamer75](https://github.com/mpgamer75)
- Expertise: Cybersecurity, Penetration Testing, Red Team Operations

## Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) - Subfinder, Nuclei
- [OWASP](https://owasp.org/) - Security resources
- [SecLists](https://github.com/danielmiessler/SecLists) - Wordlists
- [Nmap](https://nmap.org/) - Network scanning
- Open source security community

## Support

Need help?

1. Check [troubleshooting section](#troubleshooting)
2. Read [documentation](README.md) (French version)
3. Search [existing issues](https://github.com/mpgamer75/security-scanner/issues)
4. Open [new issue](https://github.com/mpgamer75/security-scanner/issues/new)

## Statistics

```
Lines of Code: 3,700+
Supported Tools: 20+
Scan Types: 4
Unit Tests: 32
Performance Gain: 80%
Report Success Rate: 100%
ShellCheck: Clean
```

---

<p align="center">
  <strong>Security Scanner v2.4.0</strong><br>
  Professional Red Team Assessment Tool<br>
  Fast - Reliable - Comprehensive
</p>

<p align="center">
  Made with care for the security community
</p>
