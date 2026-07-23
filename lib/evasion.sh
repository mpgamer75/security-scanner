# shellcheck shell=bash
# =============================================================================
# lib/evasion.sh — firewall/IDS and WAF evasion flag builders.
#
# Replaces the previous "stealth = just -T2" behavior with real evasion, and
# stops applying the loud --defeat-rst-ratelimit in stealth. Profiles:
#   none  - no evasion (fast/aggressive/quick)
#   low   - source-port + host randomization
#   med   - + fragmentation + decoy padding
#   high  - decoys, MTU frag, source-port, scan-delay, capped rate (stealth)
# All builders are pure (echo a flag string); the caller assembles the command.
# =============================================================================

# nmap_evasion_flags <profile>
nmap_evasion_flags() {
    case "$1" in
        low)
            echo "--source-port 53 --randomize-hosts"
            ;;
        med)
            echo "-f --source-port 53 --data-length 24 --randomize-hosts --max-retries 1"
            ;;
        high)
            echo "--mtu 24 --data-length 25 --source-port 53 --randomize-hosts --scan-delay 250ms --max-rate 100 -D RND:8"
            ;;
        *)
            echo ""
            ;;
    esac
}

# nmap_timing_flags <mode> : timing template per scan mode.
nmap_timing_flags() {
    case "$1" in
        quick|aggressive) echo "-T5" ;;
        stealth) echo "-T1" ;;
        *) echo "-T4" ;;
    esac
}

# mode_to_evasion <mode> : default evasion profile for a scan mode.
mode_to_evasion() {
    case "$1" in
        stealth) echo high ;;
        quick|aggressive) echo none ;;
        *) echo low ;;
    esac
}

# waf_evasion_profile <wafw00f-detection-string> : escalate web evasion when a
# WAF is present so scans are not immediately blocked/blacklisted.
waf_evasion_profile() {
    local waf="$1"
    if [ -z "$waf" ]; then
        echo low
        return
    fi
    case "$waf" in
        *[Nn]o\ WAF*|*none*|*None*) echo low ;;
        *) echo high ;;
    esac
}

# gobuster_evasion_flags <profile>
gobuster_evasion_flags() {
    case "$1" in
        high) echo "--delay 400ms --random-agent" ;;
        med) echo "--delay 150ms --random-agent" ;;
        *) echo "" ;;
    esac
}

# nuclei_evasion_flags <profile>
nuclei_evasion_flags() {
    case "$1" in
        high) echo "-rate-limit 10 -concurrency 10 -jitter 30" ;;
        med) echo "-rate-limit 40 -concurrency 15" ;;
        *) echo "" ;;
    esac
}
