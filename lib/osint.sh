#!/bin/bash
# ===================================================================
# Security Scanner - OSINT & Information Gathering Module
# ===================================================================
# Sourced by the main security script. Do not run directly.
# Requires: execute_scan(), OUTDIR, color variables from main script.
# ===================================================================

run_osint_scans() {
    local target="$1"
    local domain="$2"

    # Step total (keep in sync with the execute_scan calls below). Enrichers are
    # only counted when their API key is configured, so the counter is exact.
    local _is_ip=0
    printf '%s' "$target" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' && _is_ip=1
    local _t=0
    [ -n "$domain" ] && _t=$((_t + 6))                       # whois, dns, consolidation, crt, dorks, wayback
    [ -n "$target" ] && _t=$((_t + 2))                       # reverse-dns, geolocation
    [ "$_is_ip" = 1 ] && _t=$((_t + 1))                      # shodan internetdb (passive)
    [ "$_is_ip" = 1 ] && [ -n "$(get_key SHODAN_API_KEY)" ] && _t=$((_t + 1))
    [ "$_is_ip" = 1 ] && [ -n "$(get_key CENSYS_API_ID)" ] && [ -n "$(get_key CENSYS_API_SECRET)" ] && _t=$((_t + 1))
    [ -n "$domain" ] && [ -n "$(get_key HUNTER_API_KEY)" ] && _t=$((_t + 1))
    [ -n "$domain" ] && [ -n "$(get_key VIRUSTOTAL_API_KEY)" ] && _t=$((_t + 1))
    [ -n "$domain" ] && [ -n "$(get_key SECURITYTRAILS_API_KEY)" ] && _t=$((_t + 1))
    ui_phase_begin "OSINT & RECONNAISSANCE" "$_t"

    if [ -n "$domain" ]; then
        execute_scan "WHOIS Lookup" \
            "whois '$domain' 2>/dev/null || echo 'WHOIS query failed'" \
            $TIMEOUT_SHORT "$OUTDIR/osint/whois.txt"
        
        # Complete DNS enumeration - all record types
        execute_scan "DNS Enumeration" \
            "echo '=== A Records ===' && dig +short '$domain' A 2>/dev/null
             echo -e '\n=== MX Records ===' && dig +short '$domain' MX 2>/dev/null
             echo -e '\n=== NS Records ===' && dig +short '$domain' NS 2>/dev/null
             echo -e '\n=== TXT Records ===' && dig +short '$domain' TXT 2>/dev/null
             echo -e '\n=== AAAA Records ===' && dig +short '$domain' AAAA 2>/dev/null
             echo -e '\n=== CNAME Records ===' && dig +short '$domain' CNAME 2>/dev/null
             echo -e '\n=== SOA Record ===' && dig +short '$domain' SOA 2>/dev/null" \
            $TIMEOUT_SHORT "$OUTDIR/osint/dns_enum.txt"
        
        # Subdomain enumeration - parallel execution for speed
        echo -e "${CYAN}[INFO]${NC} Running subdomain enumeration tools in parallel..."

        # Launch all tools in background for parallel execution
        (
            if command -v subfinder &> /dev/null; then
                subfinder -d "$domain" -all -silent -t 50 -timeout 5 2>/dev/null | head -500 > "$OUTDIR/osint/subdomains_subfinder.txt" || echo 'Subfinder failed' > "$OUTDIR/osint/subdomains_subfinder.txt"
            fi
        ) &
        local subfinder_pid=$!

        (
            if command -v assetfinder &> /dev/null; then
                timeout 120 assetfinder --subs-only "$domain" 2>/dev/null | head -500 > "$OUTDIR/osint/subdomains_assetfinder.txt" || echo 'Assetfinder failed' > "$OUTDIR/osint/subdomains_assetfinder.txt"
            fi
        ) &
        local assetfinder_pid=$!

        (
            if command -v findomain &> /dev/null; then
                timeout 90 findomain -t "$domain" -q 2>/dev/null | head -500 > "$OUTDIR/osint/subdomains_findomain.txt" || echo 'Findomain failed' > "$OUTDIR/osint/subdomains_findomain.txt"
            fi
        ) &
        local findomain_pid=$!

        # Wait for all parallel processes to complete
        echo -e "${YELLOW}⏳${NC} Waiting for parallel subdomain enumeration..."
        wait $subfinder_pid 2>/dev/null && echo -e "${GREEN}[DONE]${NC} Subfinder completed" || echo -e "${RED}[FAIL]${NC} Subfinder failed"
        wait $assetfinder_pid 2>/dev/null && echo -e "${GREEN}[DONE]${NC} Assetfinder completed" || echo -e "${RED}[FAIL]${NC} Assetfinder failed"
        wait $findomain_pid 2>/dev/null && echo -e "${GREEN}[DONE]${NC} Findomain completed" || echo -e "${RED}[FAIL]${NC} Findomain failed"
        
        # Consolidate all subdomains into a single deduplicated file
        execute_scan "Subdomain Consolidation" \
            "cat $OUTDIR/osint/subdomains_*.txt 2>/dev/null | sort -u | grep -v '^$' | grep -v 'failed' > $OUTDIR/osint/all_subdomains.txt
             total_subs=\$(wc -l < $OUTDIR/osint/all_subdomains.txt 2>/dev/null || echo 0)
             echo \"Total unique subdomains: \$total_subs\"
             echo
             echo '=== Top 20 Subdomains ==='
             head -20 $OUTDIR/osint/all_subdomains.txt 2>/dev/null || echo 'No subdomains found'" \
            $TIMEOUT_SHORT "$OUTDIR/osint/subdomain_summary.txt"
        
        # Certificate transparency via crt.sh
        execute_scan "Certificate Transparency" \
            "curl -m 30 -s 'https://crt.sh/?q=%.$domain&output=json' 2>/dev/null | \
             grep -oP '\"name_value\":\"\\K[^\"]+' | sed 's/\\*\\.//g' | sort -u | head -300 || \
             echo 'Certificate transparency lookup failed'" \
            $TIMEOUT_SHORT "$OUTDIR/osint/crt_sh.txt"
        
        # theHarvester removed - public sources no longer reliable
        # For email harvesting, use alternatives like hunter.io
        echo -e "${YELLOW}[INFO]${NC} Email harvesting: Use hunter.io or alternative tools"
        
        # Google dork generation - comprehensive query list
        execute_scan "Google Dork Generation" \
            "cat > $OUTDIR/osint/google_dorks.txt << 'DORKS_END'
=== GOOGLE DORKS FOR $domain ===

--- Document Discovery ---
site:$domain filetype:pdf
site:$domain filetype:doc OR filetype:docx
site:$domain filetype:xls OR filetype:xlsx
site:$domain filetype:ppt OR filetype:pptx
site:$domain filetype:txt
site:$domain filetype:csv
site:$domain filetype:xml
site:$domain filetype:json

--- Admin Panels & Login Pages ---
site:$domain inurl:admin
site:$domain inurl:administrator
site:$domain inurl:login
site:$domain inurl:signin
site:$domain inurl:auth
site:$domain inurl:dashboard
site:$domain inurl:panel
site:$domain inurl:cpanel
site:$domain inurl:controlpanel
site:$domain inurl:adminpanel

--- Configuration & Sensitive Files ---
site:$domain inurl:config
site:$domain inurl:backup
site:$domain inurl:database
site:$domain inurl:db
site:$domain inurl:sql
site:$domain filetype:sql
site:$domain filetype:env
site:$domain filetype:log
site:$domain filetype:bak
site:$domain inurl:conf
site:$domain ext:cfg

--- Directory Listings ---
site:$domain intitle:\"index of\"
site:$domain intitle:\"directory listing\"
site:$domain intitle:\"parent directory\"

--- Error Pages & Debug Info ---
site:$domain intext:\"error\"
site:$domain intext:\"warning\"
site:$domain intext:\"debug\"
site:$domain intext:\"stack trace\"
site:$domain intext:\"fatal error\"

--- API & Development ---
site:$domain inurl:api
site:$domain inurl:v1
site:$domain inurl:v2
site:$domain inurl:rest
site:$domain inurl:graphql
site:$domain inurl:swagger

--- Credentials & Secrets ---
site:$domain intext:password
site:$domain intext:username
site:$domain intext:api_key
site:$domain intext:secret
site:$domain intext:token

--- Source Code Leaks ---
site:$domain inurl:.git
site:$domain inurl:.svn
site:$domain inurl:.env

--- Cloud Storage ---
site:*.s3.amazonaws.com \"$domain\"
site:*.blob.core.windows.net \"$domain\"
DORKS_END
cat $OUTDIR/osint/google_dorks.txt" \
            $TIMEOUT_VERY_SHORT "$OUTDIR/osint/google_dorks.txt"
        
        # Shodan removed - requires paid API key
        # To use Shodan, visit https://www.shodan.io/
        echo -e "${YELLOW}[INFO]${NC} Shodan search: Requires API key - visit https://www.shodan.io/"
        
        # Retrieve archived URLs from Wayback Machine
        execute_scan "Wayback Machine URLs" \
            "echo '=== Wayback Machine Historical URLs ===' && \
             curl -m 45 -s 'http://web.archive.org/cdx/search/cdx?url=*.$domain/*&output=text&fl=original&collapse=urlkey' 2>/dev/null | \
             head -200 || echo 'Wayback Machine lookup failed'" \
            $TIMEOUT_SHORT "$OUTDIR/osint/wayback_urls.txt"
        
        # Social media reconnaissance removed - manual OSINT recommended for targeted campaigns
    fi
    
    if [ -n "$target" ]; then
        # Reverse DNS and geolocation are independent passive lookups — run them
        # concurrently (collision-safe compact output via lib/ui.sh).
        run_scan_group "IP intelligence" \
            "_osint_reverse_dns '$target'" \
            "_osint_geolocation '$target'"
    fi

    # Optional key-gated enrichment (Shodan / Censys / hunter.io / VirusTotal /
    # SecurityTrails). Missing keys skip cleanly.
    run_osint_enrichers "$target" "$domain"

    echo -e "${GREEN}[COMPLETE]${NC} OSINT phase completed"
}

# --- Independent passive lookups (used by run_scan_group) --------------------
_osint_reverse_dns() {
    execute_scan "Reverse DNS Lookup" \
        "dig +short -x '$1' 2>/dev/null || echo 'No PTR record found'" \
        "$TIMEOUT_SHORT" "$OUTDIR/osint/reverse_dns.txt"
}

_osint_geolocation() {
    execute_scan "IP Geolocation" \
        "curl -m 10 -s 'http://ip-api.com/json/$1' 2>/dev/null || echo 'Geolocation lookup failed'" \
        "$TIMEOUT_VERY_SHORT" "$OUTDIR/osint/geolocation.txt"
}

# --- Key-gated OSINT enrichers ----------------------------------------------
# Each is enabled only if its API key is present; results are appended into the
# existing osint/*.txt files so the report parsers ingest them unchanged.
run_osint_enrichers() {
    local target="$1" domain="$2" key cid csec
    local is_ip=0
    printf '%s' "$target" | grep -qE '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$' && is_ip=1

    # Shodan InternetDB — keyless, passive (CVEs/ports/tags for an IP).
    if [ "$is_ip" = 1 ]; then
        execute_scan "Shodan InternetDB (passive)" \
            "curl -m 15 -s 'https://internetdb.shodan.io/$target' 2>/dev/null || echo 'InternetDB lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/shodan_internetdb.txt"
    fi

    # Shodan host (API key).
    key="$(get_key SHODAN_API_KEY)"
    if [ "$is_ip" = 1 ] && [ -n "$key" ]; then
        execute_scan "Shodan Host (API)" \
            "curl -m 20 -s 'https://api.shodan.io/shodan/host/$target?key=$key' 2>/dev/null || echo 'Shodan API lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/shodan_host.txt"
    elif [ "$is_ip" = 1 ]; then
        echo -e "${YELLOW}[SKIP]${NC} Shodan API (no key) — run: security config set SHODAN_API_KEY <key>"
    fi

    # Censys host (API id + secret).
    cid="$(get_key CENSYS_API_ID)"; csec="$(get_key CENSYS_API_SECRET)"
    if [ "$is_ip" = 1 ] && [ -n "$cid" ] && [ -n "$csec" ]; then
        execute_scan "Censys Host (API)" \
            "curl -m 20 -s -u '$cid:$csec' 'https://search.censys.io/api/v2/hosts/$target' 2>/dev/null || echo 'Censys lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/censys_host.txt"
    fi

    # hunter.io — emails for a domain (appended to emails.txt for the parser).
    key="$(get_key HUNTER_API_KEY)"
    if [ -n "$domain" ] && [ -n "$key" ]; then
        execute_scan "hunter.io Emails (API)" \
            "curl -m 20 -s 'https://api.hunter.io/v2/domain-search?domain=$domain&api_key=$key' 2>/dev/null | \
             grep -oE '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}' | sort -u | tee -a '$OUTDIR/osint/emails.txt' || echo 'hunter.io lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/hunter_emails.txt"
    elif [ -n "$domain" ]; then
        echo -e "${YELLOW}[SKIP]${NC} hunter.io emails (no key) — run: security config set HUNTER_API_KEY <key>"
    fi

    # VirusTotal — passive subdomains (appended to all_subdomains.txt).
    key="$(get_key VIRUSTOTAL_API_KEY)"
    if [ -n "$domain" ] && [ -n "$key" ]; then
        execute_scan "VirusTotal Subdomains (API)" \
            "curl -m 20 -s -H 'x-apikey: $key' 'https://www.virustotal.com/api/v3/domains/$domain/subdomains?limit=200' 2>/dev/null | \
             grep -oE '\"id\"[[:space:]]*:[[:space:]]*\"[^\"]+\"' | sed -E 's/.*\"([^\"]+)\"\$/\\1/' | sort -u | tee -a '$OUTDIR/osint/all_subdomains.txt' || echo 'VirusTotal lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/virustotal_subdomains.txt"
    fi

    # SecurityTrails — subdomains (appended to all_subdomains.txt).
    key="$(get_key SECURITYTRAILS_API_KEY)"
    if [ -n "$domain" ] && [ -n "$key" ]; then
        execute_scan "SecurityTrails Subdomains (API)" \
            "curl -m 20 -s -H 'APIKEY: $key' 'https://api.securitytrails.com/v1/domain/$domain/subdomains?children_only=false' 2>/dev/null | \
             grep -oE '\"[a-zA-Z0-9_-]+\"' | tr -d '\"' | sed 's/\$/.$domain/' | sort -u | tee -a '$OUTDIR/osint/all_subdomains.txt' || echo 'SecurityTrails lookup failed'" \
            "$TIMEOUT_SHORT" "$OUTDIR/osint/securitytrails_subdomains.txt"
    fi
}
