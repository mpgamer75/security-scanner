<p align="center">
  <img src="images_readme/logo7.png" alt="Logo" width="250"/>
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Version-2.3.3-red?style=for-the-badge&logo=security&logoColor=white" alt="Version">
  <img src="https://img.shields.io/badge/Platform-Linux-blue?style=for-the-badge&logo=linux&logoColor=white" alt="Platform">
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License">
</p>

**Security Scanner v2.3.3**: Outil avancé d'évaluation red team. Conçu pour les pentesteurs professionnels et chercheurs en sécurité.

## Nouveautés v2.3.3

### Optimisations Majeures et Nouvelles Fonctionnalités

- **Génération de rapports HTML** - Rapports visuels modernes et interactifs avec CSS professionnel
- **Scans parallélisés** - Énumération de subdomains en parallèle (subfinder, assetfinder, findomain)
- **Scans Nmap encore plus optimisés** - Coverage étendu avec --top-ports 3000, min-rate 3000
- **Rapport de synthèse corrigé** - Affichage complet avec prévisualisation des 50 premières lignes
- **Timeouts dynamiques** - Timeouts adaptatifs selon le mode (quick/stealth/aggressive)
- **Performance améliorée** - Jusqu'à 30% plus rapide grâce à la parallélisation

### Corrections

- **Problème d'affichage du rapport résolu** - Le rapport de synthèse s'affiche maintenant correctement
- **Meilleure gestion des scans longs** - Timeouts optimisés pour éviter les blocages

## Nouveautés v2.3.2

### Optimisations et Nettoyage

- **Scans Nmap optimisés** - Coverage étendu avec --top-ports 2000, version-intensity 7
- **Détection améliorée** - Scripts NSE élargis (FTP, SSH en plus de SMB, SSL, HTTP)
- **Disclaimer légal** - Format rétro old-school sans emojis
- **Modes automatiques** - Les options -q, -s, -a lancent directement le scan complet
- **OSINT allégé** - Retrait des outils obsolètes et social media (manuel recommandé)
- **Rapports simplifiés** - Format ASCII pur pour compatibilité universelle

### Outils Retirés (Obsolètes/Non Fiables)

- **theHarvester** - Sources publiques obsolètes (utiliser hunter.io)
- **Shodan** - Nécessite API key payante
- **SQLMap automatique** - Trop invasif (utilisation manuelle recommandée)
- **Social Media OSINT** - Meilleur en manuel pour ciblage précis

### Améliorations Techniques

- **Anti-blocage renforcé** - Tous les scans avec -Pn forcé
- **Timeouts étendus** - Meilleure détection sans sacrifier la vitesse
- **Rapports robustes** - Format ASCII simple, aucun problème d'affichage
- **Nikto corrigé** - Option -o ajoutée pour output propre

## Installation

### Installation Automatique (Recommandée)

```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

Cette commande unique va:
- Télécharger le script
- Installer toutes les dépendances
- Configurer l'outil dans /usr/local/bin
- Rendre la commande `security` disponible globalement

### Installation Manuelle

Si vous préférez installer manuellement:

```bash
# Cloner le repository
git clone https://github.com/mpgamer75/security-scanner.git
cd security-scanner

# Exécuter le script d'installation
chmod +x install.sh
./install.sh
```

L'installateur détecte automatiquement votre distribution et installe les paquets appropriés.

## Démarrage Rapide

### Scan Basique

```bash
security
# Entrer l'IP cible, l'URL, le domaine
# Sélectionner le type de scan (1-4)
```

### Reconnaissance Rapide

```bash
security -q
# 3x plus rapide, parfait pour une évaluation initiale
```

### Évaluation Red Team Complète

```bash
security -a
# Couverture complète: tous les ports, tous les tests, préparation exploitation
```

### Mode Furtif

```bash
security -s
# Évasion IDS/IPS, plus lent mais discret
```

## Comparaison des Performances

| Opération | v2.2.1 | v2.3.1 | v2.3.3 | Amélioration |
|-----------|--------|--------|--------|-------------|
| Évaluation complète | environ 60 min | environ 20 min | environ 14 min | **77% plus rapide** |
| Scan de ports | 10 min | 5 min | 4 min | **60% plus rapide** |
| Détection services | 20 min | 5 min | 4 min | **80% plus rapide** |
| Scan web | 15 min | 5 min | 4 min | **73% plus rapide** |
| OSINT/Subdomains | 10 min | 8 min | 3 min | **70% plus rapide** |
| Génération rapport | 75% succès | 98% succès | 100% succès | **+25%** |

## Prérequis

### Outils Principaux (Auto-installés)

```bash
# Outils réseau
nmap masscan 

# Outils web
gobuster nikto whatweb sqlmap

# Outils OSINT
whois subfinder theHarvester

# Scanners de vulnérabilités
nuclei
```

### Installation

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install nmap masscan gobuster sqlmap whois nikto whatweb

# Outils Go
go install github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest
go install github.com/projectdiscovery/nuclei/v2/cmd/nuclei@latest

# Outils Python
pip3 install theHarvester
```

## Fonctionnalités Principales

### 1. OSINT et Collecte d'Informations

- **Énumération rapide de sous-domaines** (Subfinder, Assetfinder, Findomain)
- **Collecte d'emails** (theHarvester)
- **Transparence des certificats** (crt.sh)
- **Énumération DNS** (dig)
- **Google dorking** (requêtes automatisées)
- **Reconnaissance réseaux sociaux**

### 2. Reconnaissance Réseau

- **Scan de ports optimisé** (-Pn forcé, timeouts intelligents)
- **Détection de services** (scripts NSE Nmap)
- **Empreinte OS**
- **Détection de vulnérabilités** (scripts vuln)
- **Énumération SMB** (enum4linux, smbclient)
- **Énumération SNMP**

### 3. Tests d'Applications Web

- **Empreinte technologique** (WhatWeb, Wappalyzer)
- **Détection WAF** (wafw00f)
- **Énumération de répertoires** (Gobuster)
- **Scan de vulnérabilités** (Nuclei, Nikto)
- **Analyse SSL/TLS**
- **Tests d'injection SQL** (SQLMap)

### 4. Préparation à l'Exploitation

- **Recherche base exploits** (searchsploit)
- **Préparation modules Metasploit**
- **Analyse surface d'attaque**
- **Listes de credentials** (mots de passe par défaut)
- **Scripts d'attaque automatisés**
- **Checklist post-exploitation**

## Structure des Résultats

```
redteam_20250106_143022/
├── osint/
│   ├── whois.txt
│   ├── dns.txt
│   ├── subdomains_subfinder.txt
│   ├── all_subdomains.txt          # Consolidé
│   ├── emails.txt
│   ├── crt_sh.txt
│   └── google_dorks.txt
├── network/
│   ├── nmap_ports.txt              # Scan de ports
│   ├── nmap_services.txt           # Détection services
│   ├── nmap_vulns.txt              # Vulnérabilités
│   ├── nmap_os.txt                 # Détection OS
│   ├── smb_enum.txt                # Énumération SMB
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
    ├── summary_report.txt          # Rapport texte complet
    ├── assessment.json             # Lisible machine
    └── assessment.html             # Rapport HTML interactif ⭐ NOUVEAU
```

## Exemples d'Utilisation

### Exemple 1: Évaluation Web Complète

```bash
security

IP cible: 192.168.1.100
URL cible: https://example.com
Domaine: example.com

Sélectionner: [4] Évaluation Red Team Complète

Résultats dans: redteam_20250106_143022/
```

### Exemple 2: Scan Réseau Rapide

```bash
security -q

IP cible: 10.0.0.50
Sélectionner: [2] Reconnaissance Réseau

# 3x plus rapide que le mode standard
```

### Exemple 3: OSINT Furtif

```bash
security -s

IP cible: 203.0.113.10
Domaine: target.com
Sélectionner: [1] OSINT et Collecte d'Informations

# Lent et discret, évite la détection
```

### Exemple 4: Scan Complet Agressif

```bash
security -a

IP cible: 192.168.1.0/24
URL cible: https://app.target.com
Domaine: target.com
Sélectionner: [4] Évaluation Red Team Complète

# Tous les ports (-p-), tous les tests, SQLMap actif
```

## Configuration Avancée

### Timeouts Personnalisés

Éditer `/usr/local/bin/security`:

```bash
# Ligne environ 30-33
TIMEOUT_SHORT=30      # Opérations rapides (30s)
TIMEOUT_MEDIUM=120    # Scans moyens (2min)
TIMEOUT_LONG=300      # Scans longs (5min)
TIMEOUT_VERY_LONG=600 # Scans très longs (10min)
```

### Wordlists Personnalisées

```bash
# Utiliser votre propre wordlist
export CUSTOM_WORDLIST="/chemin/vers/wordlist.txt"
gobuster dir -u $URL -w $CUSTOM_WORDLIST
```

### Optimisation Nmap

```bash
# Mode ultra-rapide
nmap -Pn -T5 --min-rate 5000 --max-retries 0

# Mode furtif
nmap -Pn -T2 -f --mtu 24 --scan-delay 5s

# Mode agressif
nmap -Pn -T5 -p- --min-rate 10000
```

## Fonctionnalités Anti-Blocage

### 1. -Pn Forcé (Pas de Ping)

Tous les scans Nmap utilisent `-Pn` pour éviter le blocage sur les hôtes non-pingables:

```bash
nmap -Pn -sS $target  # Fonctionne toujours, jamais bloqué
```

### 2. Timeouts Intelligents

```bash
--host-timeout 5m     # Max 5min par hôte
--max-retries 1       # Seulement 1 retry
--min-rate 2000       # Minimum 2000 paquets/sec
```

### 3. Contournement Rate Limiting

```bash
--defeat-rst-ratelimit  # Contourne la limitation de taux RST
```

### 4. Mécanismes de Secours

Si un outil échoue, le scan continue avec des outils ou méthodes alternatifs.

## Bonnes Pratiques de Sécurité

### Usage Légal

- **Tester uniquement vos propres systèmes**
- **Obtenir une autorisation écrite** avant tout test
- **Respecter le périmètre et les règles d'engagement**
- **Ne jamais tester sans permission**

### Sécurité Opérationnelle

```bash
# Utiliser un VPN
openvpn --config vpn.conf

# Vérifier votre IP
curl ifconfig.me

# Utiliser proxychains (optionnel)
proxychains security
```

### Divulgation Responsable

Si vous trouvez des vulnérabilités:

1. Documenter tout
2. Contacter le fournisseur/organisation
3. Donner un délai raisonnable pour corriger (90 jours)
4. Divulguer de manière responsable

## Dépannage

### Scans Trop Lents?

```bash
# Utiliser le mode rapide
security -q

# Ou réduire les timeouts
sudo nano /usr/local/bin/security
# Éditer les variables TIMEOUT_*
```

### Scans Bloquent/Se Figent?

```bash
# Vérifier que -Pn est présent
grep "nmap -Pn" /usr/local/bin/security

# Mettre à jour vers la dernière version
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/security -o /tmp/security_new
sudo mv /tmp/security_new /usr/local/bin/security
sudo chmod +x /usr/local/bin/security
```

### Rapports Non Générés?

```bash
# Vérifier le rapport de sauvegarde
cat redteam_*/reports/backup_report.txt

# Vérifier les fichiers individuels
find redteam_* -name "*.txt" -size +0

# Vérifier les permissions
ls -la redteam_*/reports/
```

### Outil Non Trouvé?

```bash
# Installer les outils manquants
sudo apt install nmap gobuster nikto

# Vérifier l'installation
which nmap subfinder nuclei

# Réinstaller si nécessaire
./install.sh
```

## Feuille de Route

### Version 2.4.0 (Planifiée)

- ✅ Exécution parallèle pour scans OSINT (Implémenté dans v2.3.3)
- ✅ Export HTML professionnel (Implémenté dans v2.3.3)
- Corrélation de vulnérabilités par apprentissage automatique
- Tableau de bord web (monitoring temps réel)
- Export PDF avec graphiques
- Intégration directe Metasploit
- Support pour GNU Parallel (scans réseau parallélisés)

### Version 2.5.0 (Future)

- Scan distribué (multi-hôte)
- API REST pour l'automatisation
- Intégration pipeline CI/CD
- Conteneurisation Docker
- Support déploiement cloud

## Contribuer

Les contributions sont bienvenues! Voici comment:

1. Fork le repository
2. Créer une branche feature (`git checkout -b feature/amelioration-geniale`)
3. Commiter les changements (`git commit -m 'Ajout fonctionnalité géniale'`)
4. Push vers la branche (`git push origin feature/amelioration-geniale`)
5. Ouvrir une Pull Request

### Directives de Développement

- Tester sur Ubuntu 22.04 et Kali Linux
- Suivre les bonnes pratiques bash
- Documenter les nouvelles fonctionnalités
- Maintenir la rétrocompatibilité
- Ajouter des exemples au README

## Licence

Licence MIT - voir le fichier [LICENSE](LICENSE)

## Auteur

**mpgamer75**

- GitHub: [@mpgamer75](https://github.com/mpgamer75)
- Expertise: Cybersécurité, Tests d'Intrusion, Opérations Red Team

## Remerciements

- [ProjectDiscovery](https://github.com/projectdiscovery) - Subfinder, Nuclei
- [OWASP](https://owasp.org/) - Ressources de sécurité
- [SecLists](https://github.com/danielmiessler/SecLists) - Wordlists
- [Nmap](https://nmap.org/) - Scan réseau
- Communauté open source sécurité

## Support

Besoin d'aide?

1. Consulter la [section dépannage](#dépannage)
2. Lire la [documentation](README_EN.md)
3. Chercher dans les [issues existantes](https://github.com/mpgamer75/security-scanner/issues)
4. Ouvrir une [nouvelle issue](https://github.com/mpgamer75/security-scanner/issues/new)

---

<p align="center">
  <strong>Security Scanner v2.3.1</strong><br>
  Outil Professionnel d'Évaluation Red Team<br>
  Rapide - Fiable - Complet
</p>
