# CHANGELOG

## [2.4.0] - 2026-03-22

### MAJOR FEATURES

#### Modular Architecture
- **Modularized codebase**: Split monolithic 1,868-line script into 5 sourced modules
  - `security` (874 lines): Core framework, report generation, main()
  - `lib/osint.sh` (192 lines): WHOIS, DNS, subdomains, crt.sh
  - `lib/network.sh` (217 lines): Port scanning, service detection, web discovery
  - `lib/web.sh` (229 lines): Technology fingerprinting, WAF, SSL, directory enumeration, vulnerability scanning
  - `lib/exploit.sh` (415 lines): Searchsploit, Metasploit prep, credentials, post-exploitation
- **Flexible module loading**: Searches `$SCRIPT_DIR/lib/`, `/usr/local/lib/`, `~/.local/lib/` with graceful fallback

#### Security Hardening
- **XSS prevention**: HTML reports now use `html.escape()` for all user-controlled data
- **Input validation**: New `validate_ip()`, `validate_domain()`, `validate_url()`, `validate_target()` functions with regex
- **Secure file permissions**: `umask 077` for owner-only access on scan output directories
- **JSON injection prevention**: New `json_escape()` function for safe JSON output
- **Error visibility**: Replaced blanket `2>/dev/null` with `error.log` redirection for diagnostics

#### HTML Report Overhaul
- **Light/dark mode**: Toggle with `prefers-color-scheme` support and localStorage persistence
- **Scroll progress bar**: Visual indicator at top of page
- **Accessibility**: Skip-nav link, ARIA roles (`tablist`, `tab`, `tabpanel`), `aria-selected`, `aria-controls`, `:focus-visible` outlines, `aria-hidden` on decorative icons
- **Global search**: Filter all findings with `/` keyboard shortcut
- **Severity filters**: Buttons (All/Critical/High/Medium) per section
- **Copy-to-clipboard**: Per-finding button with toast notification
- **SVG donut chart**: Vulnerability severity distribution visualization

#### Structured Logging
- **Timestamped log**: `init_logging()`, `log_info()`, `log_warn()`, `log_error()` write to `reports/scanner.log`
- **Error tracking**: Scan errors captured in `error.log` instead of silently suppressed

#### CI/CD & Testing
- **GitHub Actions CI**: ShellCheck, pylint, smoke tests, XSS verification, Bandit security scan
- **Unit tests**: 32 tests in `tests/test_html_generator.py` (all passing)
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
