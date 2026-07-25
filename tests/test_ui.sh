#!/usr/bin/env bash
# Unit tests for lib/ui.sh — colours, layout helpers, and the non-TTY scan runner.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$DIR/helpers.sh"
# shellcheck source=/dev/null
source "$ROOT/lib/ui.sh"

echo "ui:"

# Under a captured (non-TTY) stdout, ui_init must select the non-TTY path.
ui_init
assert_eq "0" "$UI_TTY" "ui_init detects non-tty under captured stdout"

# Spinner frame set depends on locale: 10 braille frames on UTF-8, 4 ASCII else.
LANG="en_US.UTF-8" LC_ALL="en_US.UTF-8" LC_CTYPE="" ui_init
assert_eq "10" "$UI_NFRAMES" "UTF-8 locale selects the 10-frame braille spinner"
assert_eq "0" "$UI_ASCII" "UTF-8 locale is not ASCII mode"
LANG="C" LC_ALL="C" LC_CTYPE="" ui_init
assert_eq "4" "$UI_NFRAMES" "non-UTF-8 locale falls back to the 4-frame ASCII spinner"
assert_eq "1" "$UI_ASCII" "C locale is ASCII mode"
unset LC_ALL LC_CTYPE; LANG="en_US.UTF-8"

# --- colour control ---------------------------------------------------------
NO_COLOR=1 ui_init
assert_eq "" "$RED" "NO_COLOR blanks the palette"
assert_eq "0" "$UI_COLOR" "NO_COLOR sets UI_COLOR=0"
unset NO_COLOR
ui_init --no-color
assert_eq "" "$GREEN" "--no-color blanks the palette"
UI_NO_COLOR=0
FORCE_COLOR=1 ui_init
assert_contains "$RED" "31" "FORCE_COLOR restores the palette even off-tty"
unset FORCE_COLOR
UI_NO_COLOR=0

# --- layout helpers ---------------------------------------------------------
ui_init --no-color   # colourless so assertions are byte-exact
UI_NO_COLOR=0
assert_eq "abc   " "$(_ui_pad 'abc' 6)" "_ui_pad pads to width"
assert_eq "toolong" "$(_ui_pad 'toolong' 4)" "_ui_pad never truncates"

UI_STEP=3; UI_PHASE_TOTAL=12
assert_eq "[03/12]" "$(_ui_step_tag)" "step tag shows NN/TT with total"
UI_PHASE_TOTAL=0
assert_eq "[03]" "$(_ui_step_tag)" "step tag shows NN without total"

rule="$(ui_rule 'NETWORK RECON')"
assert_contains "$rule" "NETWORK RECON" "ui_rule includes the title"
assert_contains "$rule" "$UI_DASH$UI_DASH" "ui_rule draws a dashed rule"

# --- execute_scan (non-tty path) --------------------------------------------
if command -v timeout >/dev/null 2>&1; then
    tmp="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/ui_test_$$")"; mkdir -p "$tmp"
    SCAN_INTERRUPTED=false
    OUTDIR="$tmp"

    out="$(execute_scan "Echo Step" "printf 'line1\nline2\n'" 10 "$tmp/echo.txt" 2>&1)"
    assert_contains "$out" "Echo Step" "execute_scan prints the step name"
    assert_eq "line1" "$(head -1 "$tmp/echo.txt")" "execute_scan captures command stdout"
    assert_contains "$out" "lines" "execute_scan prints a result row with line count"

    # A non-critical empty step returns 0; a critical empty step returns 1.
    set +e
    execute_scan "Empty NonCrit" "true" 10 "$tmp/empty1.txt" false >/dev/null 2>&1
    rc_noncrit=$?
    execute_scan "Empty Crit" "true" 10 "$tmp/empty2.txt" true >/dev/null 2>&1
    rc_crit=$?
    set -e 2>/dev/null || true
    assert_eq "0" "$rc_noncrit" "non-critical empty step returns 0"
    assert_eq "1" "$rc_crit" "critical empty step returns 1"

    # --resume skips a step whose output already exists.
    printf 'cached\n' > "$tmp/cached.txt"
    UI_RESUME=1
    out="$(execute_scan "Cached Step" "echo SHOULD_NOT_RUN > $tmp/cached.txt" 10 "$tmp/cached.txt" 2>&1)"
    UI_RESUME=0
    assert_contains "$out" "cached" "resume marks the step cached"
    assert_eq "cached" "$(cat "$tmp/cached.txt")" "resume does not re-run the command"

    rm -rf "$tmp" 2>/dev/null || true
else
    echo "  (skipping execute_scan tests — 'timeout' not available)"
fi

finish
