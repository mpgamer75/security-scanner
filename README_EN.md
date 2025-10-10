<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.3.2-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**Security Scanner v2.3.2**: Advanced red team assessment tool. Designed for professional penetration testers and security researchers.

> **Note**: The summary report (summary_report.txt) currently has display issues. A fix is being implemented for version 2.3.3. Meanwhile, consult the individual files in the osint/, network/, web/ and exploit/ folders.

## What's New in v2.3.2

### Optimizations and Cleanup

- **Optimized Nmap scans** - Extended coverage with --top-ports 2000, version-intensity 7
- **Enhanced detection** - Expanded NSE scripts (FTP, SSH in addition to SMB, SSL, HTTP)
- **Legal disclaimer** - Retro old-school format without emojis
- **Automatic modes** - Options -q, -s, -a now directly launch full assessment
- **Streamlined OSINT** - Removed obsolete tools and social media (manual recommended)
- **Simplified reports** - Pure ASCII format for universal compatibility

### Removed Tools (Obsolete/Unreliable)

- **theHarvester** - Obsolete public sources (use hunter.io instead)
- **Shodan** - Requires paid API key
- **Automatic SQLMap** - Too invasive (manual use recommended)
- **Social Media OSINT** - Better performed manually for precise targeting

### Technical Improvements

- **Enhanced anti-blocking** - All scans with forced -Pn
- **Extended timeouts** - Better detection without sacrificing speed
- **Robust reports** - Simple ASCII format, no display issues
- **Nikto fixed** - Added -o option for clean output

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

### Manual Installation

If you prefer to install manually:

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

| Operation | v2.2.1 | v2.3.1 | Improvement |
|-----------|--------|--------|-------------|
| Full assessment | approximately 60 min | approximately 20 min | **67% faster** |
| Port scanning | 10 min | 5 min | **50% faster** |
| Service detection | 20 min | 5 min | **75% faster** |
| Web scanning | 15 min | 5 min | **67% faster** |
| Report generation | 75% success | 98% success | **+23%** |

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

# Go tools
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

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
redteam_20250106_143022/
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
    ├── executive_summary.txt       # Human-readable
    └── assessment.json             # Machine-readable
```

## Usage Examples

### Example 1: Complete Web Assessment

```bash
security

Target IP: 192.168.1.100
Target URL: https://example.com
Domain: example.com

Select: [4] Complete Red Team Assessment

Results in: redteam_20250106_143022/
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

### Example 4: Aggressive Full Scan

```bash
security -a

Target IP: 192.168.1.0/24
Target URL: https://app.target.com
Domain: target.com
Select: [4] Complete Red Team Assessment

# All ports (-p-), all tests, SQLMap active
```

## Advanced Configuration

### Custom Timeouts

Edit `/usr/local/bin/security`:

```bash
# Line approximately 30-33
TIMEOUT_SHORT=30      # Quick operations (30s)
TIMEOUT_MEDIUM=120    # Medium scans (2min)
TIMEOUT_LONG=300      # Long scans (5min)
TIMEOUT_VERY_LONG=600 # Very long scans (10min)
```

### Custom Wordlists

```bash
# Use your own wordlist
export CUSTOM_WORDLIST="/path/to/wordlist.txt"
gobuster dir -u $URL -w $CUSTOM_WORDLIST
```

### Nmap Optimization

```bash
# Ultra-fast mode
nmap -Pn -T5 --min-rate 5000 --max-retries 0

# Stealth mode
nmap -Pn -T2 -f --mtu 24 --scan-delay 5s

# Aggressive mode
nmap -Pn -T5 -p- --min-rate 10000
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
# Check backup report
cat redteam_*/reports/backup_report.txt

# Check individual files
find redteam_* -name "*.txt" -size +0

# Verify permissions
ls -la redteam_*/reports/
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

### Version 2.4.0 (Planned)

- [ ] True parallel execution (GNU Parallel)
- [ ] Machine learning vulnerability correlation
- [ ] Web dashboard (real-time monitoring)
- [ ] Multi-format export (CSV, HTML, PDF)
- [ ] Direct Metasploit integration

### Version 2.5.0 (Future)

- [ ] Distributed scanning (multi-host)
- [ ] REST API for automation
- [ ] CI/CD pipeline integration
- [ ] Docker containerization
- [ ] Cloud deployment support

## Contributing

Contributions welcome! Here's how:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

### Development Guidelines

- Test on Ubuntu 22.04 and Kali Linux
- Follow bash best practices
- Document new features
- Keep backwards compatibility
- Add examples to README

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
2. Read [documentation](README_EN.md)
3. Search [existing issues](https://github.com/mpgamer75/security-scanner/issues)
4. Open [new issue](https://github.com/mpgamer75/security-scanner/issues/new)

## Statistics

```
Lines of Code: 1,563+
Supported Tools: 20+
Scan Types: 4
Performance Gain: 67%
Report Success Rate: 98%
Active Users: Growing
```

---

<p align="center">
  <strong>Security Scanner v2.3.1</strong><br>
  Professional Red Team Assessment Tool<br>
  Fast - Reliable - Comprehensive
</p>

<p align="center">
  Made with care for the security community
</p>