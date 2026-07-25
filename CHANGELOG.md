# CHANGELOG

## [2.4.0] - 2026-07-25 — completion pass

Finishes the v2.4 plan. Focus: the live running UI, a more dynamic/correct HTML report,
API-key handling, and English documentation.

### Running UI (new `lib/ui.sh`)
- **Fixed the broken spinner**: it now animates smoothly (10 fps) and is tied to the real
  command completion (removed the `kill -0 $$` no-op and the 1 fps stutter).
- **TTY / `NO_COLOR` aware**: no carriage-returns or control characters on pipes/CI; honors
  `NO_COLOR`, `--no-color`, and `FORCE_COLOR`; ASCII spinner fallback on non-UTF-8 locales.
- **Aligned phase headers** (replacing the mis-padded box headers) with per-step counters
  (`[04/12]`) and aligned `✔/✗/⧖` result rows.
- **Cursor is restored** on interrupt/exit.

### CLI, config & API keys
- **`security config` subcommand** (`list|set|get|path`) backed by `lib/config.sh`; keys are
  stored in `~/.config/security-scanner/config.env` (0600 in a 0700 dir), masked in `list`.
- **Install-time key prompts** (skippable per key and overall) in `install.sh`.
- **Key-gated OSINT enrichers**: Shodan (+ keyless InternetDB), Censys, hunter.io,
  VirusTotal, SecurityTrails — skipped cleanly when no key is set.
- **New flags**: `-o/--output`, `-p/--phases`, `--resume`, `--no-color`.
- **`--resume DIR`** reuses a previous output dir and skips completed steps.

### Parallelism
- `run_scan_group` runs independent steps concurrently (bounded by `--max-parallel`) with a
  collision-safe compact display; wired into the OSINT IP-intel and web-fingerprint phases.

### HTML report (more dynamic + exact)
- Live "showing X of Y" count, clickable status readout (severity stats filter; PORTS/SUBS/
  ATT&CK jump), Clear-filters control, sort-direction arrows, spine dimming for the active
  filter, `/` to focus search + Esc to clear, and a risk gauge that animates 0→score
  (reduced-motion safe). Verified in-browser (light + dark).
- Also emits `reports/findings.json` (the machine-readable contract).

### Correctness / cleanup
- Removed stale references to `auto_attack.sh` and "run automated attacks / persistence
  (7 methods)" in help and reports; corrected SSH/FTP MITRE technique IDs.
- Fixed `uninstall.sh` scan-results cleanup (matched `security_scan_*` but the scanner writes
  `redteam_*/`); bumped its version string; warns that removing config deletes API keys.
- Documentation rewritten in **English** (`README.md`); `README_EN.md` is now a pointer.
- CI runs the full `tests/run.sh` and shellchecks `uninstall.sh`.

### Tests
- New `tests/test_ui.sh`, `tests/test_config.sh`, extended parallel/wiring/report tests
  (139 bash assertions + 88 Python tests).

## [2.4.0] - 2026-03-22

### MAJOR FEATURES

#### Modular Architecture
- **Modularized codebase**: Split monolithic 1,868-line script into 5 sourced modules
  - `security` (874 lines): Core framework, report generation, main()
  - `lib/osint.sh` (192 lines): WHOIS, DNS, subdomains, crt.sh
  - `lib/network.sh` (217 lines): Port scanning, service detection, web discovery
  - `lib/web.sh` (229 lines): Technology fingerprinting, WAF, SSL, directory enumeration, vulnerability scanning
  - `lib/exploit.sh`: vulnerability indicators + MITRE ATT&CK defensive guidance (no exploits)
- **Flexible module loading**: Searches `$SCRIPT_DIR/lib/`, `/usr/local/lib/`, `~/.local/lib/` with graceful fallback

#### Security Hardening
- **XSS prevention**: HTML reports now use `html.escape()` for all user-controlled data
- **Input validation**: New `validate_ip()`, `validate_domain()`, `validate_url()`, `validate_target()` functions with regex
- **Secure file permissions**: `umask 077` for owner-only access on scan output directories
- **JSON injection prevention**: New `json_escape()` function for safe JSON output
- **Error visibility**: Replaced blanket `2>/dev/null` with `error.log` redirection for diagnostics

#### HTML Report Overhaul
- **Offline, self-contained**: system font stack, no CDN — renders air-gapped
- **Severity-spine layout**: a left vertical severity bar that doubles as a filter-nav
- **Light/dark mode**: `prefers-color-scheme` + localStorage persistence
- **Calibrated risk model**: real severity/CVE/CVSS taxonomy (replaces substring counting)
- **Client-side search / severity-filter / sort** and collapsible per-finding evidence
- **MITRE ATT&CK coverage matrix** + Navigator layer export (`navigator.json`)
- **Exports**: structured JSON, Markdown, and ATT&CK layer

#### Structured Logging
- **Timestamped log**: `init_logging()`, `log_info()`, `log_warn()`, `log_error()` write to `reports/scanner.log`
- **Error tracking**: Scan errors captured in `error.log` instead of silently suppressed

#### CI/CD & Testing
- **GitHub Actions CI**: ShellCheck, pylint, smoke tests, XSS verification, Bandit security scan
- **Unit tests**: 84 Python tests in `report/tests/` + bash `lib/` module tests, run via `tests/run.sh`
- **ShellCheck clean**: All scripts pass `shellcheck -e SC2086,SC2046`

#### Docker Support
- **Dockerfile**: Kali Linux base with pinned Go tool versions
- **docker-compose.yml**: NET_RAW capability, output volume mount
- **Configuration template**: `config.yml.example` with timeouts, wordlists, API keys, scan profiles

### CODE QUALITY

#### ShellCheck Compliance
- **Exported timeout variables**: `TIMEOUT_*` vars now exported for sourced modules (SC2034)
- **Separated declarations**: All `local var=$(cmd)` patterns split into declaration + assignment (SC2155)
- **Grouped redirects**: Report generation uses single `{ ... } >> "$report"` block (SC2129)
- **Direct exit checks**: Replaced `cmd; if [ $? -eq 0 ]` with `if cmd` (SC2181)
- **Proper conditionals**: Replaced `&&/||` chains with `if/else/fi` (SC2015)

#### Codebase Improvements
- **English comments**: All French comments translated throughout codebase
- **Type hints**: Full type annotations on all `html_generator.py` functions
- **Pinned versions**: Go tools use fixed versions (subfinder v2.6.6, nuclei v3.2.4, assetfinder v0.1.1)
- **Version constant**: HTML generator uses `VERSION` constant instead of hardcoded strings

### PERFORMANCE
- **3,700+ lines of code** across all modules
- **20+ integrated tools**
- **4 scan modes**: Standard, Quick, Stealth, Aggressive
- **100% report generation success rate**

### COMPATIBILITY
- Ubuntu 20.04+, 22.04+
- Kali Linux 2023.x+
- Debian 11+
- Docker (Kali Linux base)
- Bash 4.0+, Python 3.8+

### MIGRATION FROM v2.3.4
- No breaking changes for CLI usage
- New `lib/` directory must be alongside `security` script or in `/usr/local/lib/`
- Run `install.sh` to set up module paths automatically

---

## [2.3.4] - 2025-03-15

### Corrections Critiques
- **Correction timeouts scans** - Alignement des timeouts bash/nmap pour eviter interruptions
- **Amelioration detection vulnerabilites** - Scans completes meme sur cibles lentes
- **Correction affichage rapport HTML** - Section "Critical Services Detected" fonctionne correctement
- **Filtrage intelligent vulnerabilites Network** - Exclusion des messages de scan
- **Visibilite des erreurs** - Suppression de 2>/dev/null pour diagnostic facilite
- **Timeouts optimises** - TIMEOUT_LONG passe a 900s (15 min) aligne avec nmap
- **Mode Quick corrige** - Timeouts dynamiques selon le mode choisi

---

## [2.3.3] - 2025-02-10

### Nouvelles Fonctionnalites
- **Generation de rapports HTML** - Rapports visuels modernes avec CSS professionnel
- **Scans parallelises** - Enumeration de subdomains en parallele (subfinder, assetfinder, findomain)
- **Scans Nmap optimises** - Coverage etendu avec --top-ports 3000, min-rate 3000
- **Rapport de synthese corrige** - Affichage complet avec previsualisation des 50 premieres lignes
- **Timeouts dynamiques** - Timeouts adaptatifs selon le mode (quick/stealth/aggressive)
- **Performance amelioree** - Jusqu'a 30% plus rapide grace a la parallelisation

### Corrections
- **Probleme d'affichage du rapport resolu**
- **Meilleure gestion des scans longs**

---

## [2.3.2] - 2025-01-10

### Optimisations et Nettoyage
- **Scans Nmap optimises** - Coverage etendu avec --top-ports 2000, version-intensity 7
- **Detection amelioree** - Scripts NSE elargis (FTP, SSH en plus de SMB, SSL, HTTP)
- **Disclaimer legal** - Format retro old-school sans emojis
- **Modes automatiques** - Les options -q, -s, -a lancent directement le scan complet
- **OSINT allege** - Retrait des outils obsoletes et social media
- **Rapports simplifies** - Format ASCII pur pour compatibilite universelle

### Outils Retires
- theHarvester, Shodan (API payante), SQLMap automatique, Social Media OSINT

---

## [2.2.1] - 2025-09-26

### Ameliorations Majeures
- Interface modernisee avec couleurs ANSI
- Menu interactif ameliore avec descriptions detaillees
- Correction theHarvester (nouvelle syntaxe)
- Enumeration de sous-domaines etendue (Assetfinder, Findomain)
- Google Dorking avance
- Scripts NSE optimises pour Nmap
- Enumeration SMB complete (MS17-010, MS08-067)
- Detection WAF amelioree
- Analyse SSL/TLS etendue
- Scripts d'attaque automatises et credentials
- Rapport JSON structure
- Support Ubuntu/Kali

---

Pour plus d'informations, consultez la documentation complete dans README.md
