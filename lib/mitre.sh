# shellcheck shell=bash
# =============================================================================
# lib/mitre.sh — ATT&CK technique lookup for exploitation *guidance*.
#
# Used by run_exploitation_guidance() to annotate findings with technique IDs,
# references, and ROE reminders — the scanner never performs these techniques.
# Mirrors report/mitre.py so bash-side guidance and the HTML report agree.
# =============================================================================

# mitre_technique_meta <id> : echo "TACTIC|Human Name" (empty if unknown).
mitre_technique_meta() {
    case "$1" in
        T1595.002) echo "TA0043|Active Scanning: Vulnerability Scanning" ;;
        T1595.003) echo "TA0043|Active Scanning: Wordlist Scanning" ;;
        T1590.002) echo "TA0043|Gather Victim Network Information: DNS" ;;
        T1592.002) echo "TA0043|Gather Victim Host Information: Software" ;;
        T1588.005) echo "TA0042|Obtain Capabilities: Exploits" ;;
        T1588.006) echo "TA0042|Obtain Capabilities: Vulnerabilities" ;;
        T1190)     echo "TA0001|Exploit Public-Facing Application (indicated)" ;;
        T1210)     echo "TA0001|Exploitation of Remote Services (indicated)" ;;
        T1110)     echo "TA0001|Brute Force (indicated)" ;;
        T1133)     echo "TA0001|External Remote Services (indicated)" ;;
        *)         echo "" ;;
    esac
}

# mitre_service_technique <service> : indicated Initial Access technique for a
# service name (as seen in nmap output). Empty when we have no mapping.
mitre_service_technique() {
    case "$1" in
        ssh|ftp|telnet|ms-wbt-server|rdp|vnc) echo T1110 ;;
        microsoft-ds|netbios-ssn|smb|mysql|ms-sql*|mssql|postgresql|postgres|oracle|mongodb|redis)
            echo T1210 ;;
        http|https|http-proxy|http-alt|ssl/http|https-alt|http-*|https-*) echo T1190 ;;
        *) echo "" ;;
    esac
}

# mitre_reference <technique_id> : canonical ATT&CK URL.
mitre_reference() {
    local id="$1"
    case "$id" in
        *.*) echo "https://attack.mitre.org/techniques/${id%%.*}/${id##*.}" ;;
        *)   echo "https://attack.mitre.org/techniques/${id}" ;;
    esac
}
