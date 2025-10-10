# Security Scanner v2.3.2 - Release Notes

## Date de Release
10 Janvier 2025

---

## Résumé
Version de nettoyage et d'optimisation majeure. Retrait des outils obsolètes, amélioration significative des capacités de détection réseau, et simplification de l'interface utilisateur pour une compatibilité universelle.

---

## Nouveautés et Améliorations

### Optimisations Nmap (Détection Réseau Améliorée)
- **Coverage étendu**: `--top-ports` augmenté de 1000 à 2000 ports en mode standard
- **Détection services**: `--version-intensity` passé de 5 à 7 avec flag `--version-all`
- **Scripts NSE élargis**: Ajout des scripts FTP et SSH aux vulnérabilités détectées (en plus de SMB, SSL, HTTP)
- **Timeouts intelligents**: Scripts NSE avec timeout étendu (90-120s) pour meilleure détection
- **Retry amélioré**: `--max-retries` augmenté de 1 à 2 pour réduire les faux négatifs
- **Vitesse optimisée**: `--min-rate` augmenté de 1000 à 2000 paquets/sec

### Interface Utilisateur
- **Disclaimer légal**: Format rétro old-school style Hydra/SQLMap sans emojis
- **Texte anglais**: Tous les messages visibles par l'utilisateur en anglais
- **Citation humoristique**: "With great power comes great... legal paperwork" - Uncle Ben, probably

### Nettoyage Outils Obsolètes
- **theHarvester**: Retiré (sources publiques Google/Bing obsolètes depuis 2023)
- **Shodan**: Retiré du scan automatique (nécessite API key payante)
- **SQLMap**: Retrait du mode automatique (trop invasif, utilisation manuelle recommandée)
- **Social Media OSINT**: Retiré (meilleur résultat en manuel pour ciblage précis)

### Modes Automatiques Fonctionnels
- **Correction critique**: Options `-q`, `-s`, `-a` lancent maintenant directement le scan complet (option 4)
- **Message auto**: Affichage "[AUTO] Automatic mode: Full Red Team assessment selected"
- **Plus de menu interactif** en mode automatique

### Corrections de Bugs
- **Nikto**: Ajout de l'option `-o` pour output file propre
- **Rapport summary**: Format ASCII pur sans caractères Unicode complexes (╔═╗║└ etc.)
- **Compatibilité**: Rapports lisibles sur tous les terminaux

### Documentation
- **README.md**: Section installation séparée (automatique vs manuelle) sans emojis
- **README_EN.md**: Version anglaise mise à jour avec même structure
- **Note d'avertissement**: Problème d'affichage summary_report documenté (fix prévu v2.3.3)
- **install.sh**: Recommandation `sudo security` pour fonctionnalité complète

---

## Problèmes Connus

### Summary Report (summary_report.txt)
Le rapport de synthèse présente des problèmes d'affichage intermittents sur certains terminaux. 

**Workaround actuel**: Consultez les fichiers individuels dans les dossiers:
- `osint/` - Reconnaissance passive
- `network/` - Scans réseau et vulnérabilités
- `web/` - Tests applications web
- `exploit/` - Scripts d'exploitation et credentials

**Status**: Correction en cours pour v2.3.3

---

## Objectifs v2.3.3 (Prochaine Release)

### Priorité Haute
1. **Fix Summary Report**
   - Réécriture complète du générateur de rapport
   - Format tabulaire simple et robuste
   - Tests sur multiples terminaux (Kali, Ubuntu, Parrot OS, Termux)
   - Génération garantie sans erreur

2. **Amélioration Output Files**
   - Nettoyage des outputs bruts (suppression des messages d'erreur inutiles)
   - Formatage cohérent de tous les fichiers de résultats
   - Ajout d'horodatage dans chaque fichier

### Priorité Moyenne
3. **Dashboard HTML**
   - Génération d'un rapport HTML interactif
   - Graphiques de vulnérabilités (Chart.js)
   - Export PDF intégré
   - Navigation facile entre sections

4. **Performance**
   - Exécution parallèle véritable avec GNU Parallel
   - Réduction du temps de scan de 20-30% supplémentaire
   - Progress bar temps réel améliorée

5. **Détection Améliorée**
   - Ajout de scripts NSE personnalisés
   - Intégration API CVE (NVD)
   - Score CVSS automatique pour chaque vulnérabilité

### Priorité Basse
6. **Features Additionnelles**
   - Mode silencieux (`--silent` flag)
   - Export JSON structuré complet
   - Intégration JIRA/GitHub Issues pour tracking
   - Support IPv6 natif

---

## Statistiques Version

| Métrique | v2.3.1 | v2.3.2 | Amélioration |
|----------|--------|--------|--------------|
| Ports scannés (standard) | 1000 | 2000 | +100% |
| Scripts NSE vulns | 3 types | 5 types | +67% |
| Outils actifs | 19 | 15 | -21% (cleanup) |
| Taux de détection | Baseline | +15-20% | Estimé |
| Faux négatifs | Baseline | -10% | Estimé |

---

## Installation

### Nouvelle Installation
```bash
curl -sSL https://raw.githubusercontent.com/mpgamer75/security-scanner/main/install.sh | bash
```

### Mise à Jour depuis v2.3.1
```bash
cd security-scanner
git pull
chmod +x install.sh
./install.sh
```

### Utilisation Recommandée
```bash
sudo security -a    # Mode agressif avec privilèges complets
```

---

## Notes pour Développeurs

### Changements Breaking
- **Aucun** - Rétrocompatible avec v2.3.1
- Les scripts d'exploitation générés conservent le même format

### Fichiers Modifiés
- `security` (script principal) - 1505 lignes
- `install.sh` - 555 lignes  
- `README.md` - 487 lignes
- `README_EN.md` - 474 lignes

### Tests Recommandés
- Scan réseau complet sur cible de test
- Vérification modes -q, -s, -a
- Test de tous les modules individuels
- Validation rapports générés

---

## Sécurité et Légalité

Ce tool est destiné **UNIQUEMENT** aux tests d'intrusion autorisés. L'utilisation sur des systèmes sans permission écrite préalable est **ILLÉGALE** dans la plupart des juridictions.

**Utilisez de manière responsable.**

---

**Version**: 2.3.2  
**Auteur**: mpgamer75  
**Licence**: MIT  

