#!/bin/bash
# ===================================================================
# Security Scanner - Network Reconnaissance Module
# ===================================================================
# Sourced by the main security script. Do not run directly.
# Requires: execute_scan(), OUTDIR, color variables from main script.
# ===================================================================

run_network_scans() {
    local target="$1"

    echo -e "\n${BRIGHT_RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_RED}║${NC}           ${ORANGE}NETWORK RECONNAISSANCE${NC}                ${BRIGHT_RED}║${NC}"
    echo -e "${BRIGHT_RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo

    # Paramètres selon le mode + profil d'évasion (lib/evasion.sh, lib/scan.sh)
    local mode; mode="$(active_mode)"
    local evasion; evasion="$(active_evasion)"
    local nmap_timing; nmap_timing="$(nmap_timing_flags "$mode")"
    local port_range="--top-ports 3000"
    local host_timeout="--host-timeout 10m"
    local max_retries="--max-retries 2"
    case "$mode" in
        quick)      port_range="--top-ports 1000"; host_timeout="--host-timeout 5m";  max_retries="--max-retries 1" ;;
        stealth)    port_range="--top-ports 1500"; host_timeout="--host-timeout 20m"; max_retries="--max-retries 2" ;;
        aggressive) port_range="-p-";              host_timeout="--host-timeout 15m"; max_retries="--max-retries 2" ;;
    esac

    # Détection du privilège : -sS (root) sinon repli -sT (fixe le bug du scan
    # marqué [DONE] alors qu'il ne trouvait aucun port sans privilège).
    local root=0
    is_root && root=1
    [ "$root" -eq 0 ] && echo -e "${YELLOW}[INFO]${NC} Non-root: TCP connect scan (-sT). Use sudo for -sS / UDP / OS detection."
    echo -e "${CYAN}[INFO]${NC} Mode: ${WHITE}$mode${NC} ${GRAY}|${NC} Evasion: ${WHITE}$evasion${NC} ${GRAY}|${NC} Target type: ${WHITE}${TARGET_TYPE:-ip}${NC}"

    # Découverte des hosts : vrai balayage pour un CIDR (sans -Pn), sinon le scan
    # de ports -Pn suffit (remplace l'ancien no-op `nmap -Pn -sn`).
    local disc_flags; disc_flags="$(host_discovery_flags "$TARGET_TYPE")"
    if [ -n "$disc_flags" ]; then
        execute_scan "Host Discovery (sweep)" \
            "nmap $disc_flags '$target' 2>/dev/null || echo 'Discovery failed'" \
            $TIMEOUT_MEDIUM "$OUTDIR/network/host_discovery.txt"
    else
        echo "Single host $target — port scan uses -Pn (assumed reachable)" > "$OUTDIR/network/host_discovery.txt"
    fi

    # RustScan if available - ultra-fast port scanning
    if command -v rustscan &> /dev/null && [ "$QUICK_MODE" = true ]; then
        execute_scan "RustScan Ultra-Fast" \
            "rustscan -a '$target' --ulimit 5000 2>/dev/null || echo 'RustScan failed'" \
            $TIMEOUT_MEDIUM "$OUTDIR/network/rustscan.txt"
    fi
    
    # Masscan high-speed scanning (aggressive mode only)
    if command -v masscan &> /dev/null && [ "$AGGRESSIVE_MODE" = true ]; then
        execute_scan "Masscan High-Speed" \
            "sudo masscan '$target' -p1-65535 --rate=10000 2>/dev/null || echo 'Masscan failed (requires root)'" \
            $TIMEOUT_LONG "$OUTDIR/network/masscan.txt"
    fi
    
    # Scan de ports principal - privilège-aware + évasion (lib/scan.sh).
    # --defeat-rst-ratelimit n'est plus appliqué qu'en mode agressif.
    local port_scan_args; port_scan_args="$(build_port_scan_args "$root" "$mode" "$evasion" "$port_range" "$host_timeout")"
    execute_scan "Port Scanning (TCP)" \
        "nmap $port_scan_args '$target'" \
        $TIMEOUT_LONG "$OUTDIR/network/nmap_ports.txt" true
    
    # Service and version detection - increased version intensity
    local service_timeout=$TIMEOUT_LONG
    local service_host_timeout="15m"
    if [ "$QUICK_MODE" = true ]; then
        service_timeout=$TIMEOUT_MEDIUM
        service_host_timeout="2m"  # Aligné avec TIMEOUT_MEDIUM (120s)
    fi

    execute_scan "Service Version Detection" \
        "nmap -Pn -sV -sC $nmap_timing --top-ports 1000 --version-intensity 7 \
         --version-all $max_retries --host-timeout $service_host_timeout '$target'" \
        $service_timeout "$OUTDIR/network/nmap_services.txt"
    
    # UDP scan on critical ports only (UDP scanning is slow)
    if [ "$QUICK_MODE" != true ]; then
        execute_scan "UDP Critical Ports" \
            "sudo nmap -Pn -sU --top-ports 20 -T4 --max-retries 0 --host-timeout 3m '$target' 2>/dev/null || \
             nmap -Pn -sU --top-ports 20 -T4 --max-retries 0 --host-timeout 3m '$target' 2>/dev/null" \
            $TIMEOUT_MEDIUM "$OUTDIR/network/nmap_udp.txt"
    fi
    
    # Target OS fingerprinting
    execute_scan "OS Fingerprinting" \
        "sudo nmap -Pn -O --osscan-guess --max-os-tries 1 --host-timeout 3m '$target' 2>/dev/null || \
         nmap -Pn -O --osscan-guess --max-os-tries 1 --host-timeout 3m '$target' 2>/dev/null" \
        $TIMEOUT_MEDIUM "$OUTDIR/network/nmap_os.txt"
    
    # Vulnerability detection with NSE scripts - extended coverage
    execute_scan "Vulnerability Detection (NSE)" \
        "nmap -Pn -sV --script 'vuln and not dos' --script-timeout 120s \
         --top-ports 1000 $max_retries --host-timeout 15m '$target'" \
        $TIMEOUT_VERY_LONG "$OUTDIR/network/nmap_vulns.txt"
    
    # NSE scripts for critical vulnerabilities (SMB, SSL, HTTP, FTP, SSH)
    execute_scan "Critical Vulnerability Scan" \
        "nmap -Pn --script 'smb-vuln-*,ssl-*,http-vuln-*,ftp-vuln-*,ssh-*' --script-timeout 90s \
         --script-args unsafe=1 --host-timeout 12m '$target'" \
        $TIMEOUT_LONG "$OUTDIR/network/nmap_critical_vulns.txt"
    
    # Complete SMB enumeration - optimized for performance
    execute_scan "SMB Enumeration (OPTIMIZED)" \
        "# Check rapide des ports SMB
         smb_check=\$(timeout 20 nmap -Pn -p 139,445 --open -T4 --min-rate 1000 '$target' 2>/dev/null | grep -E '139/tcp|445/tcp' | grep open)

         if [ -n \"\$smb_check\" ]; then
             echo 'SMB ports detected: YES'
             echo 'Open SMB ports:'
             echo \"\$smb_check\"
             echo

             # Déterminer quels ports sont ouverts pour optimiser les scans
             port_139=\$(echo \"\$smb_check\" | grep -q '139/tcp' && echo 'yes' || echo 'no')
             port_445=\$(echo \"\$smb_check\" | grep -q '445/tcp' && echo 'yes' || echo 'no')

             # Définir les ports à scanner
             if [ \"\$port_139\" = 'yes' ] && [ \"\$port_445\" = 'yes' ]; then
                 smb_ports='139,445'
             elif [ \"\$port_445\" = 'yes' ]; then
                 smb_ports='445'
             else
                 smb_ports='139'
             fi

             echo '=== SMB Version & Security ==='
             timeout 90 nmap -Pn -p \$smb_ports \
                  --script smb-protocols,smb-security-mode,smb-os-discovery \
                  --script-timeout 30s -T4 '$target' 2>/dev/null || echo 'SMB version detection timeout'
             echo

             # SMB Enumeration - seulement si port 445 ouvert
             if [ \"\$port_445\" = 'yes' ]; then
                 echo '=== SMB Shares & Users ==='
                 timeout 90 nmap -Pn -p 445 \
                      --script smb-enum-shares,smb-enum-users \
                      --script-timeout 30s -T4 '$target' 2>/dev/null || echo 'SMB enum timeout'
                 echo
             fi

             # Scan de vulnérabilités critiques - PRIORITAIRE
             echo '=== SMB Critical Vulnerabilities ==='
             timeout 120 nmap -Pn -p \$smb_ports \
                  --script smb-vuln-ms17-010,smb-vuln-ms08-067,smb-vuln-cve2009-3103 \
                  --script-timeout 25s -T4 '$target' 2>/dev/null || echo 'SMB vuln scan timeout'
             echo

             # Outils complémentaires si disponibles (en parallèle)
             if command -v smbclient &> /dev/null; then
                 echo '=== SMB Null Session Test ==='
                 timeout 25 smbclient -L '$target' -N 2>/dev/null | head -40 || echo 'SMB null session failed'
                 echo
             fi

             if command -v enum4linux &> /dev/null && [ '$AGGRESSIVE_MODE' = true ]; then
                 echo '=== Enum4linux (Aggressive Mode) ==='
                 timeout 60 enum4linux -U -S -G '$target' 2>/dev/null | head -80 || echo 'enum4linux timeout'
             fi
         else
             echo 'SMB ports (139/445): NOT OPEN or FILTERED'
             echo 'No SMB enumeration performed'
         fi" \
        $TIMEOUT_LONG "$OUTDIR/network/smb_enum.txt"
    
    # SNMP enumeration on port 161
    execute_scan "SNMP Enumeration" \
        "timeout 90 nmap -Pn -sU -p 161 --script snmp-info,snmp-sysdescr,snmp-processes,snmp-netstat \
         --script-timeout 30s '$target' 2>/dev/null || echo 'SNMP not accessible'" \
        $TIMEOUT_MEDIUM "$OUTDIR/network/snmp_enum.txt"
    
    # Banner grabbing on common ports
    execute_scan "Banner Grabbing" \
        "for port in 21 22 23 25 80 110 143 443 3306 5432 8080; do
             echo \"=== Port \$port ===\"
             timeout 5 nc -v -n -w 2 '$target' \$port 2>&1 || echo \"Port \$port: No banner\"
         done" \
        $TIMEOUT_MEDIUM "$OUTDIR/network/banner_grabbing.txt"
    
    echo -e "${GREEN}[COMPLETE]${NC} Network reconnaissance completed"
}

detect_web_services() {
    local target="$1"
    local detected_url=""

    echo -e "${CYAN}[INFO]${NC} Detecting web services on $target..."

    # Quick check for common web ports
    local web_check
    web_check=$(timeout 30 nmap -Pn -p 80,443,8080,8443 --open -T4 "$target" 2>/dev/null | grep -E '^(80|443|8080|8443)/tcp.*open')

    if echo "$web_check" | grep -q '443/tcp.*open'; then
        detected_url="https://$target"
        echo -e "${GREEN}[DETECTED]${NC} HTTPS service on port 443"
    elif echo "$web_check" | grep -q '8443/tcp.*open'; then
        detected_url="https://$target:8443"
        echo -e "${GREEN}[DETECTED]${NC} HTTPS service on port 8443"
    elif echo "$web_check" | grep -q '80/tcp.*open'; then
        detected_url="http://$target"
        echo -e "${GREEN}[DETECTED]${NC} HTTP service on port 80"
    elif echo "$web_check" | grep -q '8080/tcp.*open'; then
        detected_url="http://$target:8080"
        echo -e "${GREEN}[DETECTED]${NC} HTTP service on port 8080"
    else
        echo -e "${YELLOW}[WARN]${NC} No standard web ports detected"
        echo -e "${YELLOW}[INFO]${NC} Will attempt HTTP on port 80 anyway"
        detected_url="http://$target"
    fi

    echo "$detected_url"
}
