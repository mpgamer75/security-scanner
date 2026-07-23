#!/usr/bin/env bash
# Unit tests for lib/scan.sh (privilege-aware scan flags, host discovery).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"
# build_port_scan_args composes timing/evasion helpers, so load that module too.
# shellcheck source=lib/evasion.sh
source "$DIR/../lib/evasion.sh"
# shellcheck source=lib/scan.sh
source "$DIR/../lib/scan.sh"

echo "scan:"

# SYN scan needs root; fall back to connect scan otherwise (the old bug: -sS
# was always used and silently produced zero ports when unprivileged).
assert_eq "-sS" "$(nmap_scan_flag 1)" "scan-root-syn"
assert_eq "-sT" "$(nmap_scan_flag 0)" "scan-nonroot-connect"

# Base flags: skip host discovery on the port scan (-Pn), skip rDNS (-n),
# only report open ports (--open).
BASE="$(nmap_base_flags)"
assert_contains "$BASE" "-Pn"    "base-pn"
assert_contains "$BASE" "-n"     "base-n"
assert_contains "$BASE" "--open" "base-open"

# Host discovery: for a CIDR do a REAL sweep (no -Pn, use -PE/-PS/-PA);
# for a single host skip it (the -Pn port scan covers it).
CIDR_DISC="$(host_discovery_flags cidr)"
assert_contains     "$CIDR_DISC" "-sn" "disc-cidr-sn"
assert_not_contains "$CIDR_DISC" "-Pn" "disc-cidr-no-pn"
assert_contains     "$CIDR_DISC" "-PE" "disc-cidr-pe"
assert_eq ""        "$(host_discovery_flags ip)"       "disc-ip-skip"
assert_eq ""        "$(host_discovery_flags hostname)" "disc-host-skip"

# is_root returns 0/1 without erroring
is_root >/dev/null 2>&1
assert_contains "0 1" "$(is_root; echo $?)" "is-root-runs"

# build_port_scan_args assembles the full flag set and encodes the bug fixes.
STD="$(build_port_scan_args 1 standard none '--top-ports 3000' '--host-timeout 10m')"
assert_contains     "$STD" "-sS"                    "bps-root-syn"
assert_contains     "$STD" "-Pn"                    "bps-pn"
assert_contains     "$STD" "--open"                 "bps-open"
assert_contains     "$STD" "-T4"                    "bps-timing"
assert_not_contains "$STD" "--defeat-rst-ratelimit" "bps-std-not-loud"

NONROOT="$(build_port_scan_args 0 standard none '--top-ports 3000' '')"
assert_contains     "$NONROOT" "-sT"                "bps-nonroot-connect"
assert_not_contains "$NONROOT" "-sS"                "bps-nonroot-no-syn"

STEALTH="$(build_port_scan_args 1 stealth high '--top-ports 1500' '--host-timeout 20m')"
assert_contains     "$STEALTH" "-D RND"                 "bps-stealth-decoys"
assert_contains     "$STEALTH" "--scan-delay"           "bps-stealth-delay"
assert_not_contains "$STEALTH" "--defeat-rst-ratelimit" "bps-stealth-not-loud"
assert_not_contains "$STEALTH" "-T4"                    "bps-stealth-not-fast"

# Aggressive is the ONE mode where the loud speed flags are appropriate.
AGGR="$(build_port_scan_args 1 aggressive none '-p-' '--host-timeout 15m')"
assert_contains "$AGGR" "-T5"                    "bps-aggr-fast"
assert_contains "$AGGR" "--defeat-rst-ratelimit" "bps-aggr-loud-ok"

finish
