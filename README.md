<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Version-2.4.0-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
  <img src="https://img.shields.io/badge/Docker-Ready-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

**Security Scanner v2.4.0** — an adaptive, MITRE ATT&CK-aligned red-team reconnaissance
tool for **authorized** penetration testing and security research. It runs a full
OSINT → Network → Web → Guidance workflow and produces a self-contained, offline HTML
report plus machine-readable JSON.

> **Reconnaissance and exploitation _guidance_ only.** This tool does **not** run exploits,
> brute-force, webshells, or persistence. The "exploitation" stage produces defensive
> indicators and MITRE ATT&CK mappings for an authorized operator to act on manually.
> Use it only against systems you own or are explicitly authorized to test.

---

## Highlights (v2.4)

- **Adaptive targeting** — auto-detects and adapts to IP, CIDR, hostname, URL, or IPv6
  (no longer forces you to supply an IP).
- **Real evasion** — stealth mode applies decoys, timing, fragmentation, source-port and
  capped rate; the web scan adapts automatically when a WAF is detected.
- **MITRE ATT&CK alignment** — findings are tagged with technique IDs; the report includes
  an ATT&CK coverage matrix and exports a Navigator layer (`navigator.json`).
- **Modular engine** — the bash scanner is split into sourced `lib/*.sh` modules; all
  parsing, correlation, and reporting live in a pure-stdlib Python `report/` package.
- **Clean, honest running UI** — a TTY-aware, `NO_COLOR`-aware progress display with a
  smooth spinner tied to real completion, aligned phase headers, and per-step counters.
  On a pipe/CI it degrades to plain line-per-event output (no control characters).
- **Offline HTML report** — self-contained (no CDN/fonts), light/dark, with client-side
  search / severity-filter / sort, an animated risk gauge, evidence expanders, and JSON /
  Markdown / ATT&CK-layer exports.
- **Optional API enrichment** — Shodan, Censys, hunter.io, VirusTotal, SecurityTrails
  (plus keyless Shodan InternetDB). Missing keys are skipped cleanly.
- **Bounded parallelism** — independent scan steps run concurrently with a configurable cap.
- **Resume** — continue an interrupted run and skip already-completed steps.

## Installation

### Automatic (recommended)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

The installer detects your distribution, installs the required tools, downloads the
`security` script together with the `lib/` modules and the `report/` package into
`/usr/local/bin`, and **optionally** prompts you for API keys (every key is skippable, and
you can configure them later — see [API keys](#api-keys)).

### Manual

```bash
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner
chmod +x install.sh
./install.sh
```

### Docker

```bash
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner
docker compose up -d
docker exec -it security-scanner security -t scanme.nmap.org
```

## Uninstall

```bash
# If you cloned the repo:
./uninstall.sh

# Or remove manually:
sudo rm -f /usr/local/bin/security /usr/local/bin/html_generator.py
sudo rm -rf /usr/local/bin/lib /usr/local/bin/report
rm -rf ~/.config/security-scanner        # deletes saved API keys
```

`uninstall.sh` is interactive: it removes the executable, `lib/`, and the `report/`
package, and (with confirmation) can also remove Go tools, scan-result directories
(`redteam_*/`), the config directory (**this deletes saved API keys**), and downloaded
wordlists. Scan results and wordlists are preserved unless you opt in.

## Quick start

```bash
security                                   # interactive full assessment
security -t scanme.nmap.org                # non-interactive target (standard mode)
security -q -t 10.0.0.5                     # quick recon
security -a -t 10.0.0.0/24                  # aggressive full scan of a subnet
security -s -t example.com                  # stealth mode (IDS/IPS evasion)
security -p osint,web -d acme.io -u https://acme.io   # only the OSINT + web phases
security --resume redteam_20260725_143022  # continue an interrupted run
```

### Options

| Flag | Description |
|------|-------------|
| `-t, --target VAL` | Target: IP / CIDR / hostname / URL (auto-detected) |
| `-u, --url VAL` | Target URL for web testing |
| `-d, --domain VAL` | Target domain for OSINT |
| `-q` / `-s` / `-a` | Quick / Stealth / Aggressive mode |
| `-o, --output DIR` | Output directory (default `redteam_TIMESTAMP`) |
| `-p, --phases LIST` | Run only these phases: `osint,network,web,exploit` |
| `--evasion LEVEL` | Override evasion: `none \| low \| med \| high` |
| `--max-parallel N` | Max concurrent independent scan steps (default 4) |
| `--resume DIR` | Reuse a previous output dir; skip completed steps |
| `--no-color` | Disable color (also honors the `NO_COLOR` env var) |
| `-y, --yes` | Non-interactive; run the full assessment |

Running with `sudo` is recommended for SYN scans (`-sS`), UDP scans, and OS detection.

## API keys

Optional integrations enrich the OSINT phase. Keys are stored in
`~/.config/security-scanner/config.env` (created `0600` in a `0700` directory) and are
**never** committed. Set them during installation or any time afterwards:

```bash
security config set SHODAN_API_KEY <key>
security config list          # review which keys are set (values masked)
security config path          # print the config file path
```

Recognized keys: `SHODAN_API_KEY`, `CENSYS_API_ID`, `CENSYS_API_SECRET`, `HUNTER_API_KEY`,
`VIRUSTOTAL_API_KEY`, `SECURITYTRAILS_API_KEY`. Without a key, the corresponding enricher
is skipped with a clear notice (Shodan's keyless InternetDB lookup still runs for IPs).

## What it does

1. **OSINT** — WHOIS, DNS, subdomain enumeration (subfinder/assetfinder/findomain),
   certificate transparency (crt.sh), Google-dork generation, Wayback URLs, reverse DNS,
   geolocation, and optional key-gated enrichment.
2. **Network** — privilege-aware port scanning (`-sS` as root, `-sT` otherwise),
   service/version detection, OS fingerprinting, NSE vulnerability scripts, SMB/SNMP
   enumeration, and banner grabbing, with mode- and evasion-aware flags.
3. **Web** — technology fingerprinting (WhatWeb), WAF detection (wafw00f) with adaptive
   throttling, SSL/TLS analysis, directory enumeration (Gobuster), and vulnerability
   scanning (Nuclei, Nikto).
4. **Guidance** — per-service defensive indicators and MITRE ATT&CK mappings (detection +
   remediation). No exploits are generated or run.

## Reports

Every run writes to `redteam_TIMESTAMP/reports/`:

| File | Description |
|------|-------------|
| `assessment.html` | Self-contained, offline, interactive report (open in any browser) |
| `assessment.json` / `findings.json` | Normalized, machine-readable findings model |
| `assessment.md` | Markdown summary |
| `navigator.json` | MITRE ATT&CK Navigator layer (load at mitre-attack.github.io/attack-navigator) |
| `summary_report.txt` | Plain-text summary |
| `scanner.log` | Timestamped run log |

The HTML report is organized by **severity** (a left "severity spine" that doubles as a
filter), with a calibrated risk score, an ATT&CK coverage matrix, an attack-surface table,
OSINT assets, exploitation **guidance** (indication only), and findings-conditioned
recommendations. It works fully offline — no network requests, no external fonts.

### Output layout

```
redteam_20260725_143022/
├── osint/      whois, dns, subdomains, crt.sh, dorks, geolocation, enrichers…
├── network/    nmap_ports, nmap_services, nmap_vulns, smb_enum, snmp_enum…
├── web/        whatweb, wafw00f, ssl_analysis, gobuster, nuclei, nikto…
├── exploit/    *_indicators.txt (defensive/MITRE guidance — no attack artifacts)
└── reports/    assessment.{html,json,md}, findings.json, navigator.json, scanner.log
```

## Architecture

```
security            # thin orchestrator: arg parsing, target profiling, phase dispatch
lib/
  ui.sh             # colors/TTY/NO_COLOR, aligned headers, the spinner + execute_scan
  config.sh         # ~/.config/security-scanner/config.env, get/set keys
  targeting.sh      # profile_target(): ip|cidr|hostname|url → phase plan
  evasion.sh scan.sh# nmap/web evasion flag builders (mode + WAF aware)
  parallel.sh       # bounded concurrent job pool + run_scan_group
  osint.sh network.sh web.sh exploit.sh   # the phase functions
  mitre.sh          # ATT&CK technique lookup
report/             # pure-stdlib Python package (offline; no pip install)
  models.py severity.py parsers/*.py mitre.py collect.py render.py
  templates/{styles.css,app.js}           # inlined into the HTML (no CDN)
html_generator.py   # backward-compatible CLI shim → report.render
```

## Testing

```bash
bash tests/run.sh        # bash lib unit tests + python report unit tests
shellcheck lib/*.sh security install.sh uninstall.sh
```

The Python report package is pure standard library, so the report generates on any system
with Python 3 — no dependencies, air-gap friendly.

## Ethics & authorization

This tool is for **authorized** testing only. Evasion features (decoys, timing,
fragmentation, proxying) are standard authorized-pentest techniques, gated behind explicit
modes and accompanied by a persistent rules-of-engagement reminder. Obtain written
authorization, respect scope, and disclose responsibly. The author disclaims all
responsibility for misuse.

## License

MIT — see [LICENSE](LICENSE).

## Author

**mpgamer75** — [github.com/mpgamer75](https://github.com/mpgamer75)

## Acknowledgments

- [ProjectDiscovery](https://github.com/projectdiscovery) — subfinder, nuclei
- [Nmap](https://nmap.org/) — network scanning
- [SecLists](https://github.com/danielmiessler/SecLists) — wordlists
- [MITRE ATT&CK](https://attack.mitre.org/) — technique framework
- The open-source security community

---

<p align="center"><strong>Security Scanner v2.4.0</strong><br>Adaptive · MITRE-aligned · Offline-first</p>
