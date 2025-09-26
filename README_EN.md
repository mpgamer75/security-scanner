<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.2.1-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**Security Scanner**: An advanced reconnaissance and security assessment tool that automates OSINT phases, network reconnaissance, and web application testing. Designed for cybersecurity professionals, pentesters, and bug hunters.

## Installation

### Automatic Installation (Recommended)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

### Manual Installation

1. **Clone the repository**

```bash
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner
```

2. **Install dependencies**

```bash
chmod +x install.sh
./install.sh
```

3. **Global installation**

```bash
sudo chmod +x security
sudo mv security /usr/local/bin/
```

### Uninstallation

To completely uninstall Security Scanner:

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/uninstall.sh | bash
```

Or for manual uninstallation:

```bash
# Remove executable
sudo rm -f /usr/local/bin/security

# Remove desktop entry
rm -f ~/.local/share/applications/security-scanner.desktop

# Remove Go tools (optional)
rm -f $(go env GOPATH)/bin/{subfinder,nuclei,amass,assetfinder}
```

**Note:** Uninstallation does not automatically remove scan results or wordlists to preserve your data.

## Prerequisites

### Main Tools

- `nmap` - Port and service scanner
- `masscan` - High-speed scanner
- `subfinder` - Subdomain discovery
- `gobuster` - Directory brute forcing
- `sqlmap` - SQL injection detection
- `theHarvester` - Email and information gathering
- `whois` - Domain information
- `nikto` - Web vulnerability scanner
- `whatweb` - Technology identification
- `nuclei` - Modern vulnerability scanner

### Tool Installation (Ubuntu/Debian)

```bash
sudo apt update
sudo apt install nmap masscan gobuster sqlmap whois nikto whatweb dig openssl

# Go tools installation
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install -v github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest
```

## Main Features

### New in Version 2.2.1
- **Modernized user interface** with professional design
- **Automated attack scripts** based on scan results
- **Post-exploitation techniques** and advanced persistence
- **Extended OSINT enumeration** with new tools
- **Optimized NSE scripts** for SMB and vulnerabilities
- **Structured JSON reports** for automation
- **theHarvester compatibility** new version
- **Optional Shodan integration**
- **English interface** for international audience
- **Emoji-free professional design**

### OSINT & Information Gathering

- **WHOIS lookup** - Domain ownership information
- **DNS enumeration** - A, MX, NS, TXT records
- **SSL certificate analysis** - Certificate details
- **Subdomain discovery** - Via Subfinder, Amass, Assetfinder
- **Email harvesting** - theHarvester integration
- **Certificate transparency** - Historical certificate data
- **Social media reconnaissance** - Profile discovery
- **Google dorking** - Advanced search queries

### Network Reconnaissance

- **Optimized port scanning** - Nmap with performance profiles
- **Service detection** - Version identification
- **OS fingerprinting** - Operating system identification
- **UDP scanning** - Critical UDP ports
- **Ultra-fast Masscan** - High-speed scanning
- **SMB enumeration** - Complete SMB analysis
- **SNMP enumeration** - Network device discovery
- **Vulnerability detection** - NSE script integration

### Web Application Testing

- **Directory enumeration** - Gobuster with multiple wordlists
- **Vulnerability scanning** - Nikto and Nuclei
- **SQL injection testing** - Automated SQLMap
- **Technology identification** - WhatWeb analysis
- **SSL/TLS analysis** - Security configuration testing
- **WAF detection** - Web Application Firewall identification
- **XSS testing** - Cross-site scripting detection

### Exploitation & Red Team

- **Automated attack scripts** - Service-based exploitation
- **Post-exploitation enumeration** - System information gathering
- **Persistence techniques** - Multiple backdoor methods
- **Credential lists** - Extensive default credentials
- **Metasploit integration** - MSF module preparation
- **Attack surface analysis** - Comprehensive threat modeling

### Reports & Organization

- **Structured reports** - Detailed executive summary
- **Category organization** - OSINT, Network, Web, Exploitation
- **Timestamp format** - Scan timestamping
- **Quick analysis** - Key findings summary
- **JSON reports** - Machine-readable format
- **Report validation** - Automatic completeness checking

## Usage

### Interactive Mode

```bash
security
```

### Command Line Options

```bash
security --help      # Display help
security --version   # Display version
security --quick     # Quick scan mode
security --stealth   # Stealth scan mode
```

### Typical Workflow

1. **Launch the scanner**

   ```bash
   security
   ```

2. **Enter target information**
   - Target IP address
   - URL (optional)
   - Domain name (optional)

3. **Select scan type**
   - OSINT & Information Gathering
   - Network Reconnaissance
   - Web Application Testing
   - Complete Red Team Assessment

4. **Analyze results**
   - Check report in `redteam_assessment_YYYYMMDD_HHMMSS/`
   - Executive summary available in `reports/executive_summary.txt`

## Results Structure

```
redteam_assessment_20241226_143022/
├── osint/
│   ├── whois.txt                    # WHOIS information
│   ├── dns_enum.txt                 # Standard DNS enumeration
│   ├── subdomains_subfinder.txt     # Subdomains (Subfinder)
│   ├── subdomains_amass.txt         # Subdomains (Amass)
│   ├── subdomains_assetfinder.txt   # Subdomains (Assetfinder)
│   ├── all_subdomains.txt           # Consolidated subdomains
│   ├── emails.txt                   # Collected emails
│   ├── google_dorks.txt             # Google dorking queries
│   ├── shodan.txt                   # Shodan search results
│   ├── wayback_urls.txt             # Historical URLs
│   └── social_media.txt             # Social media profiles
├── network/
│   ├── nmap_standard.txt            # Standard Nmap scan
│   ├── nmap_services.txt            # Service detection
│   ├── nmap_vulns.txt               # Vulnerability scripts
│   ├── nmap_critical_vulns.txt      # Critical vulnerabilities
│   ├── nmap_os.txt                  # OS fingerprinting
│   ├── smb_enum.txt                 # SMB enumeration
│   └── snmp_enum.txt                # SNMP enumeration
├── web/
│   ├── whatweb.txt                  # Technology detection
│   ├── wafw00f.txt                  # WAF detection
│   ├── ssl_analysis.txt             # SSL/TLS analysis
│   ├── gobuster_common.txt          # Directory enumeration
│   ├── nuclei_comprehensive.txt     # Vulnerability scan
│   ├── nikto.txt                    # Web vulnerabilities
│   └── sqlmap/                      # SQL injection results
├── exploitation/
│   ├── searchsploit.txt             # Exploit database search
│   ├── msf_prep.txt                 # Metasploit preparation
│   ├── attack_surface.txt           # Attack surface analysis
│   ├── credentials.txt              # Default credentials
│   ├── auto_attack.sh               # Automated attack scripts
│   ├── post_exploit.sh              # Post-exploitation scripts
│   └── persistence.sh               # Persistence techniques
└── reports/
    ├── executive_summary.txt        # Executive summary report
    └── assessment_results.json      # JSON structured report
```

## Usage Examples

### Complete OSINT Scan

```bash
# Information gathering on a domain
Target: example.com
Options: 1 (OSINT & Information Gathering)
```

### In-Depth Network Reconnaissance

```bash
# Network scan of an IP address
Target: 192.168.1.100
Options: 2 (Network Reconnaissance)
```

### Web Application Testing

```bash
# Web application security testing
Target: https://example.com
Options: 3 (Web Application Testing)
```

### Complete Security Audit

```bash
# Complete assessment (OSINT + Network + Web + Exploitation)
Target IP: 192.168.1.100
Target URL: https://example.com
Domain: example.com
Options: 4 (Complete Red Team Assessment)
```

## Advanced Configuration

### Performance Optimization

**Ultra-Fast Nmap**

```bash
# Script modification for very fast scanning
nmap -n -T5 --min-rate=5000 --max-retries=1
```

**High-Speed Masscan**

```bash
# Configuration for fast networks
masscan --rate=100000 --wait=0
```

### Custom Wordlists

```bash
# Using custom wordlists
export CUSTOM_WORDLIST="/path/to/custom/wordlist.txt"
```

## Security Considerations

### Legal Usage

- Use only on your own systems
- Obtain written authorization before any testing
- Respect service terms of use
- Never use on unauthorized systems

### Best Practices

- Limit scan speed on shared networks
- Use VPNs for external testing
- Document all testing activities
- Respect responsible disclosure policies

## Warnings

> **IMPORTANT**: This tool is intended for authorized security professionals. Unauthorized use of this tool may violate local and international laws. The author disclaims all responsibility for malicious use.

## Troubleshooting

### Common Issues

**Error: "Tool not found"**

```bash
# Check tool installation
security --help
which nmap subfinder gobuster
```

**Slow scans**

```bash
# Check network connectivity
ping 8.8.8.8
# Adjust Nmap timing parameters
```

**Insufficient permissions**

```bash
# Some scans require root privileges
sudo security
```

## Future Enhancements

### Version 2.3.0 (Planned)

- [ ] Optional web interface
- [ ] Metasploit integration
- [ ] IoT vulnerability scanning
- [ ] Multi-format export (JSON, XML, CSV)
- [ ] Real-time notifications

### Version 2.4.0 (Roadmap)

- [ ] Distributed mode for large-scale scanning
- [ ] Threat intelligence integration
- [ ] REST API automation
- [ ] Monitoring dashboard

## Contributing

Contributions are welcome! Here's how to contribute:

1. **Fork** the project
2. **Create** a feature branch (`git checkout -b feature/enhancement`)
3. **Commit** your changes (`git commit -am 'Add new feature'`)
4. **Push** to the branch (`git push origin feature/enhancement`)
5. **Open** a Pull Request

### Contribution Guidelines

- Follow existing naming conventions
- Document new features
- Test on multiple Linux distributions
- Respect bash coding style

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**mpgamer75**

- GitHub: [@mpgamer75](https://github.com/mpgamer75)
- Specialty: Cybersecurity

## Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) for Subfinder and Nuclei
- [OWASP](https://owasp.org/) for security resources
- [SecLists](https://github.com/danielmiessler/SecLists) for wordlists
- The open source community for security tools

## Support

For help:

1. Check the [documentation](README_EN.md)
2. Review [existing issues](https://github.com/mpgamer75/security-scanner/issues)
3. Open a [new issue](https://github.com/mpgamer75/security-scanner/issues/new)

---

<p align="center">
  <strong>Security Scanner - Professional Security Assessment Tool</strong>
</p>
