#!/usr/bin/env bash
# Unit tests for lib/evasion.sh (nmap + web evasion flag builders).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"
# shellcheck source=lib/evasion.sh
source "$DIR/../lib/evasion.sh"

echo "evasion:"

# nmap evasion profiles
assert_eq ""             "$(nmap_evasion_flags none)"            "ev-none"
assert_contains "$(nmap_evasion_flags low)"  "--source-port 53" "ev-low-sp"
assert_contains "$(nmap_evasion_flags med)"  "-f"               "ev-med-frag"
assert_contains "$(nmap_evasion_flags med)"  "--data-length"    "ev-med-dl"

HIGH="$(nmap_evasion_flags high)"
assert_contains     "$HIGH" "-D RND"                 "ev-high-decoys"
assert_contains     "$HIGH" "--source-port 53"       "ev-high-sourceport"
assert_contains     "$HIGH" "--scan-delay"           "ev-high-delay"
assert_contains     "$HIGH" "--max-rate"             "ev-high-maxrate"
assert_not_contains "$HIGH" "--defeat-rst-ratelimit" "ev-high-not-loud"
assert_not_contains "$HIGH" "-T4"                    "ev-high-not-fast"

# timing per mode
assert_contains "$(nmap_timing_flags stealth)" "-T" "tim-stealth"
assert_eq "-T4" "$(nmap_timing_flags standard)"     "tim-standard"
assert_eq "-T5" "$(nmap_timing_flags aggressive)"   "tim-aggressive"
assert_eq "-T5" "$(nmap_timing_flags quick)"        "tim-quick"

# mode -> evasion mapping (stealth means REAL evasion now)
assert_eq high "$(mode_to_evasion stealth)"    "mte-stealth"
assert_eq none "$(mode_to_evasion aggressive)" "mte-aggressive"
assert_eq low  "$(mode_to_evasion standard)"   "mte-standard"

# WAF-aware web evasion
assert_eq high "$(waf_evasion_profile 'Cloudflare (Cloudflare Inc.)')" "waf-detected"
assert_eq low  "$(waf_evasion_profile '')"                             "waf-empty"
assert_eq low  "$(waf_evasion_profile 'No WAF detected')"              "waf-none"

# web tool evasion flags
assert_eq ""   "$(gobuster_evasion_flags none)"                    "gob-none"
assert_contains "$(gobuster_evasion_flags high)" "--delay"         "gob-delay"
assert_contains "$(gobuster_evasion_flags high)" "--random-agent"  "gob-ua"
assert_contains "$(nuclei_evasion_flags high)"   "-rate-limit"     "nuc-rl"

finish
