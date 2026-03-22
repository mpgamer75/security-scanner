# Security Scanner v2.4.0 - Release Notes

## Date de Release
22 Mars 2026

---

## Resume

Version majeure introduisant une architecture modulaire, un renforcement securitaire complet, des rapports HTML nouvelle generation avec accessibilite, le support Docker, un pipeline CI/CD, et la conformite ShellCheck sur l'ensemble du code.

---

## Nouveautes et Ameliorations

### Architecture Modulaire
- **Decoupage en modules**: Script monolithique (1,868 lignes) decoupe en 5 fichiers sources
  - `security` (874 lignes): Framework principal, generation de rapports, main()
  - `lib/osint.sh` (192 lignes): WHOIS, DNS, sous-domaines, crt.sh
  - `lib/network.sh` (217 lignes): Scan de ports, detection de services, decouverte web
  - `lib/web.sh` (229 lignes): Fingerprinting technologique, WAF, SSL, enumeration, vulns
  - `lib/exploit.sh` (415 lignes): Searchsploit, Metasploit, credentials, post-exploitation
- **Chargement flexible**: Recherche dans `$SCRIPT_DIR/lib/`, `/usr/local/lib/`, `~/.local/lib/` avec fallback gracieux

### Securite Renforcee
- **Prevention XSS**: Remplacement de l'echappement manuel `< >` par `html.escape()` dans tout le generateur HTML
- **Validation d'entree**: Nouvelles fonctions `validate_ip()`, `validate_domain()`, `validate_url()`, `validate_target()` avec regex
- **Permissions securisees**: `umask 077` pour acces proprietaire uniquement sur les repertoires de sortie
- **Prevention injection JSON**: Nouvelle fonction `json_escape()` pour sortie JSON sure
- **Visibilite des erreurs**: Remplacement de `2>/dev/null` par redirection vers `error.log`

### Rapport HTML Nouvelle Generation
- **Mode clair/sombre**: Toggle avec support `prefers-color-scheme` et persistence localStorage
- **Barre de progression**: Indicateur visuel de scroll en haut de page
- **Accessibilite complete**: Lien skip-nav, roles ARIA (tablist, tab, tabpanel), aria-selected, aria-controls, contours `:focus-visible`, aria-hidden sur icones decoratives
- **Recherche globale**: Filtrage de tous les resultats avec raccourci clavier `/`
- **Filtres par severite**: Boutons (All/Critical/High/Medium) par section
- **Copie en un clic**: Bouton copier par resultat avec notification toast
- **Graphique SVG**: Donut chart pour la distribution des severites de vulnerabilites
- **Landmarks ARIA**: role=main, role=banner, role=search, role=list, role=listitem

### Logging Structure
- **Journal horodate**: `init_logging()`, `log_info()`, `log_warn()`, `log_error()` ecrivent dans `reports/scanner.log`
- **Suivi des erreurs**: Erreurs de scan capturees dans `error.log` au lieu d'etre supprimees silencieusement

### CI/CD et Tests
- **GitHub Actions CI**: Pipeline complet avec ShellCheck, pylint, smoke tests, verification XSS, scan securite Bandit
- **32 tests unitaires**: `tests/test_html_generator.py` couvrant toutes les fonctions de generation HTML
- **ShellCheck clean**: Tous les scripts (security, install.sh, lib/*.sh) passent shellcheck sans warnings

### Docker
- **Dockerfile**: Image basee sur Kali Linux avec versions pinees des outils Go
- **docker-compose.yml**: Capacite NET_RAW, montage de volume pour sortie
- **Configuration**: Template `config.yml.example` avec timeouts, wordlists, cles API, profils de scan

### Qualite de Code
- **Commentaires en anglais**: Tous les commentaires francais traduits dans security et install.sh
- **Type hints Python**: Annotations de type completes sur toutes les fonctions html_generator.py
- **Versions pinees**: Outils Go avec versions fixes (subfinder v2.6.6, nuclei v3.2.4, assetfinder v0.1.1)
- **Constante VERSION**: Le generateur HTML utilise une constante au lieu de chaines codees en dur
- **Conformite ShellCheck**: Correction de SC2034, SC2155, SC2129, SC2181, SC2015 sur tous les fichiers

---

## Statistiques Version

| Metrique | v2.3.4 | v2.4.0 | Amelioration |
|----------|--------|--------|--------------|
| Lignes de code | 1,868 | 3,700+ | +98% |
| Fichiers source | 3 | 10+ | Architecture modulaire |
| Tests unitaires | 0 | 32 | Nouveau |
| Warnings ShellCheck | 14 | 0 | 100% clean |
| Securite XSS | Non | Oui | html.escape() |
| Validation entree | Non | Oui | Regex complete |
| Support Docker | Non | Oui | Nouveau |
| Pipeline CI/CD | Non | Oui | GitHub Actions |
| Accessibilite HTML | Basique | Complete | ARIA, skip-nav, keyboard |

---

## Installation

### Nouvelle Installation
```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

### Installation Docker
```bash
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner
docker-compose up -d
```

### Mise a Jour depuis v2.3.4
```bash
cd security-scanner
git pull
chmod +x install.sh
./install.sh
```

---

## Migration depuis v2.3.4

### Changements Breaking
- **Aucun** pour l'utilisation en ligne de commande
- Le nouveau repertoire `lib/` doit etre present a cote du script `security` ou dans `/usr/local/lib/`
- L'installateur gere automatiquement la mise en place des modules

### Fichiers Ajoutes
- `lib/osint.sh` - Module OSINT
- `lib/network.sh` - Module reseau
- `lib/web.sh` - Module web
- `lib/exploit.sh` - Module exploitation
- `.github/workflows/ci.yml` - Pipeline CI/CD
- `tests/test_html_generator.py` - Tests unitaires
- `Dockerfile` - Image Docker
- `docker-compose.yml` - Orchestration Docker
- `config.yml.example` - Template de configuration

---

## Notes pour Developpeurs

### Architecture
```
security-scanner/
├── security                    # Script principal (874 lignes)
├── lib/
│   ├── osint.sh               # Module OSINT (192 lignes)
│   ├── network.sh             # Module reseau (217 lignes)
│   ├── web.sh                 # Module web (229 lignes)
│   └── exploit.sh             # Module exploitation (415 lignes)
├── html_generator.py          # Generateur de rapports HTML (1,794 lignes)
├── install.sh                 # Script d'installation
├── tests/
│   └── test_html_generator.py # 32 tests unitaires
├── .github/workflows/
│   └── ci.yml                 # Pipeline CI/CD
├── Dockerfile                 # Image Docker
├── docker-compose.yml         # Orchestration
└── config.yml.example         # Configuration template
```

### Tests Recommandes
- Scan reseau complet sur cible de test
- Verification modes -q, -s, -a
- Test de tous les modules individuels
- Validation rapports generes (texte, JSON, HTML)
- Verification accessibilite HTML (lecteur d'ecran)
- `shellcheck -e SC2086,SC2046 security lib/*.sh install.sh`
- `python3 -m pytest tests/`

---

## Securite et Legalite

Ce tool est destine **UNIQUEMENT** aux tests d'intrusion autorises. L'utilisation sur des systemes sans permission ecrite prealable est **ILLEGALE** dans la plupart des juridictions.

**Utilisez de maniere responsable.**

---

**Version**: 2.4.0
**Auteur**: mpgamer75
**Licence**: MIT
