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
    
    echo -e "\n${BRIGHT_RED}╔════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${BRIGHT_RED}║${NC}              ${ORANGE}OSINT & RECONNAISSANCE${NC}                ${BRIGHT_RED}║${NC}"
    echo -e "${BRIGHT_RED}╚════════════════════════════════════════════════════════════╝${NC}"
    echo
    
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
        # Reverse DNS lookup on IP
        execute_scan "Reverse DNS Lookup" \
            "dig +short -x '$target' 2>/dev/null || echo 'No PTR record found'" \
            $TIMEOUT_SHORT "$OUTDIR/osint/reverse_dns.txt"
        
        # IP geolocation via ip-api
        execute_scan "IP Geolocation" \
            "curl -m 10 -s 'http://ip-api.com/json/$target' 2>/dev/null || echo 'Geolocation lookup failed'" \
            $TIMEOUT_VERY_SHORT "$OUTDIR/osint/geolocation.txt"
    fi
    
    echo -e "${GREEN}[COMPLETE]${NC} OSINT phase completed"
}
