# shellcheck shell=bash
# =============================================================================
# lib/scan.sh — privilege-aware nmap flag helpers + real host discovery.
#
# Fixes the historical recon bugs:
#   * -sS was used unconditionally; unprivileged it errors and yields 0 ports,
#     yet the step was still marked DONE. Now we pick -sS only with privilege,
#     else -sT (connect scan).
#   * Host discovery used the no-op combination `-Pn -sn`. For a CIDR we now do
#     a real ping sweep (-PE/-PS/-PA, no -Pn); for a single host we skip it.
#   * Always add -n (no rDNS) and --open (drop closed/filtered noise).
# =============================================================================

# is_root : return 0 when the effective user can raw-socket scan.
is_root() {
    [ "$(id -u 2>/dev/null || echo 1000)" -eq 0 ]
}

# nmap_scan_flag <is_root_bool> : -sS when privileged (1), else -sT.
nmap_scan_flag() {
    if [ "${1:-0}" -eq 1 ] 2>/dev/null; then
        echo "-sS"
    else
        echo "-sT"
    fi
}

# nmap_base_flags : flags applied to every port scan.
nmap_base_flags() {
    echo "-Pn -n --open"
}

# host_discovery_flags <target_type> : a real discovery sweep for ranges only.
host_discovery_flags() {
    case "$1" in
        cidr)
            echo "-sn -PE -PS21,22,80,443,3389,8080 -PA80,443 --max-retries 1"
            ;;
        *)
            echo ""
            ;;
    esac
}

# build_port_scan_args <is_root> <mode> <evasion> <port_range> <host_timeout_flag>
# Assemble the full nmap port-scan flag string. This is where the recon bug
# fixes live: connect-scan fallback, -n/--open, real evasion, and NO
# --defeat-rst-ratelimit except in the (loud, opt-in) aggressive mode.
build_port_scan_args() {
    local root="$1" mode="$2" evasion="$3" port_range="$4" host_timeout="$5"
    local parts
    parts="$(nmap_scan_flag "$root") $(nmap_base_flags) $(nmap_timing_flags "$mode") $port_range"
    local ev
    ev="$(nmap_evasion_flags "$evasion")"
    [ -n "$ev" ] && parts="$parts $ev"
    # Aggressive + no-evasion is the only place the loud speed flags belong.
    if [ "$mode" = "aggressive" ] && [ "$evasion" = "none" ]; then
        parts="$parts --min-rate 10000 --defeat-rst-ratelimit"
    fi
    [ -n "$host_timeout" ] && parts="$parts $host_timeout"
    echo "$parts" | tr -s ' '
}
