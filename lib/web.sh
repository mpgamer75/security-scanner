#!/bin/bash
# ===================================================================
# Security Scanner - Web Application Testing Module
# ===================================================================
# Sourced by the main security script. Do not run directly.
# Requires: execute_scan(), OUTDIR, color variables from main script.
# ===================================================================

run_web_scans() {
    local url="$1"

    # Validate and normalize URL
    if [ -z "$url" ]; then
        echo -e "${RED}[ERROR]${NC} URL parameter is empty"
        return 1
    fi

    # Ensure URL has protocol
    if ! echo "$url" | grep -qE '^https?://'; then
        echo -e "${YELLOW}[WARN]${NC} URL missing protocol, assuming http://"
        url="http://$url"
    fi

    local domain
    domain=$(echo "$url" | sed 's|https\?://||' | sed 's|/.*||' | sed 's|:.*||')

    # Step total (keep in sync with the execute_scan calls below).
    # Always: port-check, ssl, xss = 3.
    local _wl="/usr/share/wordlists/dirb"; [ ! -d "$_wl" ] && _wl="$HOME/.local/share/wordlists/dirb"
    local _t=3
    command -v whatweb >/dev/null 2>&1 && _t=$((_t + 1))
    command -v wafw00f >/dev/null 2>&1 && _t=$((_t + 1))
    command -v gobuster >/dev/null 2>&1 && [ -f "$_wl/common.txt" ] && _t=$((_t + 1))
    command -v gobuster >/dev/null 2>&1 && [ "$AGGRESSIVE_MODE" = true ] && [ -f "$_wl/big.txt" ] && _t=$((_t + 1))
    command -v nuclei >/dev/null 2>&1 && _t=$((_t + 1))
    command -v nikto >/dev/null 2>&1 && [ "$QUICK_MODE" != true ] && _t=$((_t + 1))
    ui_phase_begin "WEB APPLICATION TESTING" "$_t"
    echo -e "${CYAN}[TARGET]${NC} $url"

    # Quick check for open web ports
    execute_scan "Web Port Check" \
        "timeout 30 nmap -Pn -p 80,443,8080,8443 --open '$domain' 2>/dev/null | \
         grep -E 'open' || echo 'No standard web ports detected (continuing anyway)'" \
        $TIMEOUT_SHORT "$OUTDIR/web/port_check.txt"

    # Fingerprinting: WhatWeb, wafw00f and SSL/TLS analysis are independent —
    # run them concurrently, then adapt web evasion from the WAF result.
    local web_evasion; web_evasion="$(active_evasion)"
    local _fp=( "_web_ssl '$domain'" )
    command -v whatweb >/dev/null 2>&1 && _fp+=( "_web_whatweb '$url'" )
    command -v wafw00f >/dev/null 2>&1 && _fp+=( "_web_wafw00f '$url'" )
    run_scan_group "Web fingerprint" "${_fp[@]}"

    # A detected WAF means slow down + randomize UA, or risk getting blacklisted.
    if [ -f "$OUTDIR/web/wafw00f.txt" ] && grep -qi "is behind" "$OUTDIR/web/wafw00f.txt"; then
        local waf_name; waf_name="$(grep -i 'is behind' "$OUTDIR/web/wafw00f.txt" | head -1)"
        web_evasion="$(waf_evasion_profile "$waf_name")"
        echo -e "${YELLOW}[WAF]${NC} WAF detected — web evasion raised to ${WHITE}${web_evasion}${NC}"
    fi

    # Directory brute-forcing with gobuster
    local wordlist_dir="/usr/share/wordlists/dirb"
    [ ! -d "$wordlist_dir" ] && wordlist_dir="$HOME/.local/share/wordlists/dirb"
    
    if command -v gobuster &> /dev/null && [ -f "$wordlist_dir/common.txt" ]; then
        local threads=50
        local extensions="php,html,txt,js,css"
        
        if [ "$QUICK_MODE" = true ]; then
            threads=80
            extensions="php,html"
        elif [ "$AGGRESSIVE_MODE" = true ]; then
            threads=100
            extensions="php,html,txt,js,css,json,xml,asp,aspx,jsp"
        fi

        # Under WAF/high evasion: lower threads and add delay + random UA
        local gob_evasion; gob_evasion="$(gobuster_evasion_flags "$web_evasion")"
        [ "$web_evasion" = "high" ] && threads=10

        execute_scan "Directory Enumeration (Common)" \
            "gobuster dir -u '$url' -w '$wordlist_dir/common.txt' -t $threads $gob_evasion \
             -x $extensions -q --timeout 10s --no-error 2>/dev/null | head -300 || echo 'Gobuster failed'" \
            $TIMEOUT_LONG "$OUTDIR/web/gobuster_common.txt"
        
        if [ "$AGGRESSIVE_MODE" = true ] && [ -f "$wordlist_dir/big.txt" ]; then
            execute_scan "Directory Enumeration (Extended)" \
                "gobuster dir -u '$url' -w '$wordlist_dir/big.txt' -t 50 \
                 -x php,html,txt -q --timeout 10s --no-error 2>/dev/null | head -500 || echo 'Gobuster extended failed'" \
                $TIMEOUT_VERY_LONG "$OUTDIR/web/gobuster_extended.txt"
        fi
    fi
    
    # Web vulnerability scanning with Nuclei - optimized for stability
    if command -v nuclei &> /dev/null; then
        local severity="-severity critical,high,medium"
        local nuclei_timeout=$TIMEOUT_LONG
        local rate_limit="150"  # Requests per second
        local template_timeout="30"  # Timeout per template en secondes

        if [ "$QUICK_MODE" = true ]; then
            severity="-severity critical,high"
            nuclei_timeout=$TIMEOUT_MEDIUM
            rate_limit="200"
            template_timeout="20"
        elif [ "$AGGRESSIVE_MODE" = true ]; then
            severity="-severity critical,high,medium,low"
            nuclei_timeout=$TIMEOUT_VERY_LONG
            rate_limit="100"
            template_timeout="45"
        fi

        # WAF / high evasion: throttle nuclei to avoid blocking/blacklisting
        local concurrency=20
        local nuclei_extra=""
        if [ "$web_evasion" = "high" ]; then
            rate_limit=10; concurrency=10; nuclei_extra="-jitter 30"
        elif [ "$web_evasion" = "med" ]; then
            rate_limit=40; concurrency=15
        fi

        # Update templates in background (non-blocking)
        echo -e "${CYAN}[INFO]${NC} Updating Nuclei templates..."
        (nuclei -update-templates -silent &>/dev/null &)
        sleep 2  # Give templates time to start updating

        echo -e "${CYAN}[SCAN]${NC} Running Nuclei against $url"
        execute_scan "Vulnerability Scanning (Nuclei)" \
            "if timeout $nuclei_timeout nuclei -u '$url' $severity -silent \
                -timeout $template_timeout -retries 2 \
                -rate-limit $rate_limit -concurrency $concurrency $nuclei_extra \
                -no-interactsh -no-color \
                -stats -stats-interval 30 2>&1 | head -200; then
                echo 'Nuclei scan completed successfully'
             else
                exit_code=\$?
                if [ \$exit_code -eq 124 ]; then
                    echo 'Nuclei scan timed out (this is normal for large scans)'
                else
                    echo 'Nuclei scan completed with errors (code: '\$exit_code')'
                fi
             fi" \
            $((nuclei_timeout + 60)) "$OUTDIR/web/nuclei.txt"
    else
        echo -e "${YELLOW}[SKIP]${NC} Nuclei not installed"
    fi

    # Nikto web vulnerability scan - optimized
    if command -v nikto &> /dev/null && [ "$QUICK_MODE" != true ]; then
        local nikto_timeout=$TIMEOUT_LONG
        local nikto_tuning="-Tuning x"  # Generic tests

        if [ "$AGGRESSIVE_MODE" = true ]; then
            nikto_timeout=$TIMEOUT_VERY_LONG
            nikto_tuning="-Tuning 123456789ab"  # All tests
        fi

        echo -e "${CYAN}[SCAN]${NC} Running Nikto against $url"
        execute_scan "Nikto Web Vulnerability Scan" \
            "set -o pipefail
             if timeout $((nikto_timeout + 60)) nikto -h '$url' \
                -C all \
                $nikto_tuning \
                -timeout 20 \
                -maxtime $nikto_timeout \
                -nointeractive \
                -Format txt \
                -output '$OUTDIR/web/nikto_raw.txt' 2>&1 | tee '$OUTDIR/web/nikto_output.txt'; then
                 echo 'Nikto scan completed successfully'
                 [ -f '$OUTDIR/web/nikto_raw.txt' ] && cat '$OUTDIR/web/nikto_raw.txt'
             else
                 exit_code=\$?
                 if [ \$exit_code -eq 124 ]; then
                     echo 'Nikto scan timed out'
                     [ -f '$OUTDIR/web/nikto_raw.txt' ] && cat '$OUTDIR/web/nikto_raw.txt'
                 else
                     echo 'Nikto scan completed with warnings (code: '\$exit_code')'
                     [ -f '$OUTDIR/web/nikto_raw.txt' ] && cat '$OUTDIR/web/nikto_raw.txt'
                 fi
             fi" \
            $((nikto_timeout + 120)) "$OUTDIR/web/nikto.txt"
    elif [ "$QUICK_MODE" = true ]; then
        echo -e "${YELLOW}[SKIP]${NC} Nikto skipped in quick mode"
    else
        echo -e "${YELLOW}[SKIP]${NC} Nikto not installed"
    fi
    
    # SQLMap removed - requires specific configuration and can be invasive
    # For SQL injection testing, use manually:
    # sqlmap -u "URL?param=value" --batch --level=2 --risk=2
    echo -e "${YELLOW}[INFO]${NC} SQL Injection: Test manually with SQLMap if needed"
    
    # XSS payload generation for manual testing
    execute_scan "XSS Payload Generation" \
        "cat > $OUTDIR/web/xss_payloads.txt << 'XSS_END'
=== XSS TESTING PAYLOADS ===

--- Basic Payloads ---
<script>alert(1)</script>
<script>alert(document.domain)</script>
<img src=x onerror=alert(1)>
<svg onload=alert(1)>
<body onload=alert(1)>

--- HTML Context ---
\"><script>alert(1)</script>
'><script>alert(1)</script>

--- Attribute Context ---
\" onclick=alert(1) x=\"
' onclick=alert(1) x='

--- JavaScript Context ---
';alert(1);//
\";alert(1);//

--- Advanced Payloads ---
<ScRiPt>alert(1)</ScRiPt>
<img src=x onerror=\"alert('XSS')\">
<svg/onload=alert(1)>

--- Bypass Payloads ---
<script>eval(atob('YWxlcnQoMSk='))</script>
<img src=x:alert(alt) onerror=eval(src) alt=1>
XSS_END
cat $OUTDIR/web/xss_payloads.txt" \
        $TIMEOUT_VERY_SHORT "$OUTDIR/web/xss_payloads.txt"
    
    echo -e "${GREEN}[COMPLETE]${NC} Web application testing completed"
}

# --- Independent web-fingerprint tasks (used by run_scan_group) --------------
_web_whatweb() {
    execute_scan "Technology Detection (WhatWeb)" \
        "whatweb -a 3 -v --max-threads 20 '$1' 2>/dev/null || echo 'WhatWeb failed'" \
        "$TIMEOUT_MEDIUM" "$OUTDIR/web/whatweb.txt"
}

_web_wafw00f() {
    execute_scan "WAF Detection (wafw00f)" \
        "wafw00f '$1' 2>/dev/null || echo 'wafw00f failed'" \
        "$TIMEOUT_SHORT" "$OUTDIR/web/wafw00f.txt"
}

_web_ssl() {
    execute_scan "SSL/TLS Analysis" \
        "echo '=== Certificate Information ==='
         echo | timeout 20 openssl s_client -connect '$1:443' -servername '$1' 2>/dev/null | \
         openssl x509 -text 2>/dev/null | head -50 || echo 'SSL connection failed'
         echo
         echo '=== Cipher Suites ==='
         timeout 90 nmap -Pn --script ssl-enum-ciphers -p 443 '$1' 2>/dev/null | head -80 || echo 'SSL cipher scan failed'
         echo
         echo '=== SSL Vulnerabilities ==='
         timeout 90 nmap -Pn --script ssl-heartbleed,ssl-poodle,ssl-ccs-injection,ssl-dh-params \
              -p 443 '$1' 2>/dev/null || echo 'SSL vuln scan failed'
         if command -v sslscan &> /dev/null; then
             echo
             echo '=== SSLScan Results ==='
             timeout 60 sslscan '$1' 2>/dev/null | head -100 || echo 'sslscan failed'
         fi" \
        "$TIMEOUT_LONG" "$OUTDIR/web/ssl_analysis.txt"
}
