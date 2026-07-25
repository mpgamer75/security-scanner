#!/usr/bin/env bash
# Integration test: source the real security script (main is guarded) and verify
# the lib modules are sourced and the mode/evasion glue works end-to-end.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"

# Colors the script expects to exist before sourcing.
NC='' RED='' YELLOW='' CYAN='' WHITE='' GRAY='' GREEN='' BRIGHT_RED='' ORANGE='' DARK_RED='' BOLD='' DIM=''
# shellcheck source=security
source "$DIR/../security" >/dev/null 2>&1

echo "security wiring:"

# lib functions are available after sourcing the script
for fn in build_port_scan_args profile_target nmap_evasion_flags run_parallel active_mode active_evasion; do
    assert_eq yes "$(command -v "$fn" >/dev/null 2>&1 && echo yes || echo no)" "fn-$fn"
done

# UI + config + phase wiring are sourced from lib/ (ui.sh, config.sh) and defined.
for fn in execute_scan ui_init ui_phase_begin ui_rule run_scan_group config_cmd get_key load_config run_selected_phases; do
    assert_eq yes "$(command -v "$fn" >/dev/null 2>&1 && echo yes || echo no)" "fn-$fn"
done

# mode + evasion glue
QUICK_MODE=false; STEALTH_MODE=false; AGGRESSIVE_MODE=false; EVASION_OVERRIDE=""
assert_eq standard "$(active_mode)"     "mode-standard"
assert_eq low      "$(active_evasion)"  "evasion-standard"

STEALTH_MODE=true
assert_eq stealth "$(active_mode)"    "mode-stealth"
assert_eq high    "$(active_evasion)" "evasion-stealth"

STEALTH_MODE=false; EVASION_OVERRIDE=high
assert_eq high "$(active_evasion)" "evasion-override"
EVASION_OVERRIDE=""

# real port-scan assembly through the script's own functions
STEALTH_PS="$(build_port_scan_args 1 stealth high '--top-ports 1500' '')"
assert_contains     "$STEALTH_PS" "-D RND"                 "ps-stealth-decoys"
assert_not_contains "$STEALTH_PS" "--defeat-rst-ratelimit" "ps-stealth-not-loud"

finish
