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

    echo -e "\n${BRIGHT_RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_RED}║${NC}         ${ORANGE}WEB APPLICATION TESTING${NC}               ${BRIGHT_RED}║${NC}"
    echo -e "${BRIGHT_RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    echo -e "${CYAN}[TARGET]${NC} $url"
    echo

    local domain
    domain=$(echo "$url" | sed 's|https\?://||' | sed 's|/.*||' | sed 's|:.*||')
    
    # Quick check for open web ports
    execute_scan "Web Port Check" \
        "timeout 30 nmap -Pn -p 80,443,8080,8443 --open '$domain' 2>/dev/null | \
         grep -E 'open' || echo 'No standard web ports detected (continuing anyway)'" \
        $TIMEOUT_SHORT "$OUTDIR/web/port_check.txt"
    
    # Web technology detection with WhatWeb
    if command -v whatweb &> /dev/null; then
        execute_scan "Technology Detection (WhatWeb)" \
            "whatweb -a 3 -v --max-threads 20 '$url' 2>/dev/null || echo 'WhatWeb failed'" \
            $TIMEOUT_MEDIUM "$OUTDIR/web/whatweb.txt"
    fi
    
    # WAF detection with wafw00f
    if command -v wafw00f &> /dev/null; then
        execute_scan "WAF Detection (wafw00f)" \
            "wafw00f '$url' 2>/dev/null || echo 'wafw00f failed'" \
            $TIMEOUT_SHORT "$OUTDIR/web/wafw00f.txt"
    fi
    
    # Comprehensive SSL/TLS analysis (certificates, ciphers, vulnerabilities)
    execute_scan "SSL/TLS Analysis" \
        "echo '=== Certificate Information ==='
         echo | timeout 20 openssl s_client -connect '$domain:443' -servername '$domain' 2>/dev/null | \
         openssl x509 -text 2>/dev/null | head -50 || echo 'SSL connection failed'
         echo
         echo '=== Cipher Suites ==='
         timeout 90 nmap -Pn --script ssl-enum-ciphers -p 443 '$domain' 2>/dev/null | head -80 || echo 'SSL cipher scan failed'
         echo
         echo '=== SSL Vulnerabilities ==='
         timeout 90 nmap -Pn --script ssl-heartbleed,ssl-poodle,ssl-ccs-injection,ssl-dh-params \
              -p 443 '$domain' 2>/dev/null || echo 'SSL vuln scan failed'
         if command -v sslscan &> /dev/null; then
             echo
             echo '=== SSLScan Results ==='
             timeout 60 sslscan '$domain' 2>/dev/null | head -100 || echo 'sslscan failed'
         fi" \
        $TIMEOUT_LONG "$OUTDIR/web/ssl_analysis.txt"
    
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
        
        execute_scan "Directory Enumeration (Common)" \
            "gobuster dir -u '$url' -w '$wordlist_dir/common.txt' -t $threads \
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

        # Update templates in background (non-blocking)
        echo -e "${CYAN}[INFO]${NC} Updating Nuclei templates..."
        (nuclei -update-templates -silent &>/dev/null &)
        sleep 2  # Give templates time to start updating

        echo -e "${CYAN}[SCAN]${NC} Running Nuclei against $url"
        execute_scan "Vulnerability Scanning (Nuclei)" \
            "if timeout $nuclei_timeout nuclei -u '$url' $severity -silent \
                -timeout $template_timeout -retries 2 \
                -rate-limit $rate_limit -concurrency 20 \
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
