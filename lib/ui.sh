# shellcheck shell=bash
# =============================================================================
# lib/ui.sh — terminal UI: colors, aligned rules, and the scan runner.
#
# Sourced FIRST by `security` (before osint/network/web/exploit, which all call
# execute_scan). Everything terminal-facing lives here so behaviour is
# consistent and testable:
#   - TTY detection ([ -t 1 ]) and NO_COLOR / --no-color support
#   - a smooth spinner tied to the *real* command completion (not a decoupled
#     0.5s busy-wait, and not the old `kill -0 $$` no-op)
#   - visible-width-aligned result rows and phase headers (no more mis-padded
#     box-drawing headers)
#   - a compact, collision-safe mode for parallel scan groups
#
# Requires (from the main script, best-effort): OUTDIR, SCAN_INTERRUPTED,
# log_info/log_warn. All are optional — ui.sh degrades if they are absent.
# =============================================================================

# ---- Palette ----------------------------------------------------------------
# Defined here (real ESC bytes) so ui_init can blank them for NO_COLOR / non-TTY.
ui_define_colors() {
    RED=$'\033[0;31m';       DARK_RED=$'\033[38;5;124m'; ORANGE=$'\033[38;5;208m'
    BRIGHT_RED=$'\033[1;31m'; YELLOW=$'\033[1;33m';       GREEN=$'\033[0;32m'
    CYAN=$'\033[0;36m';      WHITE=$'\033[1;37m';        GRAY=$'\033[0;90m'
    DIM=$'\033[2m';          BOLD=$'\033[1m';            NC=$'\033[0m'
}

ui_disable_colors() {
    RED=''; DARK_RED=''; ORANGE=''; BRIGHT_RED=''; YELLOW=''; GREEN=''
    CYAN=''; WHITE=''; GRAY=''; DIM=''; BOLD=''; NC=''
}

# ui_init [--no-color]
# Establishes UI_TTY, colour state, spinner frames and result glyphs. Safe to
# call more than once (e.g. before the banner, after parsing --no-color).
ui_init() {
    [ "${1:-}" = "--no-color" ] && UI_NO_COLOR=1

    UI_TTY=0; [ -t 1 ] && UI_TTY=1

    # UTF-8 locale? If not, fall back to ASCII spinner/glyphs so non-UTF-8
    # terminals don't render mojibake.
    case "${LC_ALL:-${LC_CTYPE:-${LANG:-}}}" in
        *UTF-8*|*utf-8*|*UTF8*|*utf8*) UI_ASCII=0 ;;
        *) UI_ASCII=1 ;;
    esac
    [ "${UI_FORCE_ASCII:-0}" = 1 ] && UI_ASCII=1

    local want_color=1
    [ -n "${NO_COLOR:-}" ] && want_color=0          # https://no-color.org
    [ "${UI_NO_COLOR:-0}" = 1 ] && want_color=0     # --no-color flag
    [ "$UI_TTY" -eq 0 ] && [ -z "${FORCE_COLOR:-}" ] && want_color=0
    if [ "$want_color" -eq 1 ]; then ui_define_colors; else ui_disable_colors; fi
    UI_COLOR="$want_color"

    if [ "$UI_ASCII" -eq 1 ]; then
        UI_FRAMES=('|' '/' '-' "\\")
        UI_OK='+'; UI_BAD='x'; UI_TIMEOUT='~'; UI_STOP='!'; UI_RUN='>'; UI_DASH='-'
    else
        UI_FRAMES=('⠋' '⠙' '⠹' '⠸' '⠼' '⠴' '⠦' '⠧' '⠇' '⠏')
        UI_OK='✔'; UI_BAD='✗'; UI_TIMEOUT='⧖'; UI_STOP='■'; UI_RUN='▷'; UI_DASH='─'
    fi
    UI_NFRAMES=${#UI_FRAMES[@]}

    UI_PHASE_NAME=''; UI_PHASE_TOTAL=0; UI_STEP=0; UI_PARALLEL=0
    : "${UI_RESUME:=0}"
    return 0
}

# Restore the cursor (called on exit / interrupt so a killed spinner can't leave
# the cursor hidden).
ui_cleanup() {
    [ "${UI_TTY:-0}" = 1 ] && printf '\033[?25h' 2>/dev/null
    return 0
}

# ---- Layout helpers ---------------------------------------------------------
_ui_repeat() {  # _ui_repeat <char> <n>
    local ch="$1" n="$2" out=''
    while [ "$n" -gt 0 ]; do out="$out$ch"; n=$((n - 1)); done
    printf '%s' "$out"
}

ui_term_width() {
    local w="${COLUMNS:-0}"
    if [ "$w" -le 0 ] && [ "${UI_TTY:-0}" -eq 1 ] && command -v tput >/dev/null 2>&1; then
        w="$(tput cols 2>/dev/null || echo 0)"
    fi
    [ "$w" -le 0 ] 2>/dev/null && w=72
    [ "$w" -gt 100 ] && w=100
    printf '%s' "$w"
}

# ui_rule ["TITLE"] — a full-width titled rule (replaces the hand-padded boxes).
ui_rule() {
    local title="${1:-}" width dash
    width="$(ui_term_width)"
    dash="${UI_DASH:--}"
    if [ -z "$title" ]; then
        printf '%b%s%b\n' "${GRAY:-}" "$(_ui_repeat "$dash" "$width")" "${NC:-}"
        return 0
    fi
    local lead used rest
    lead="$(_ui_repeat "$dash" 2)"
    used=$(( 4 + ${#title} ))          # "── " + title + " "
    rest=$(( width - used )); [ "$rest" -lt 3 ] && rest=3
    printf '%b%s %b%s%b %b%s%b\n' \
        "${GRAY:-}" "$lead" "${BOLD:-}${ORANGE:-}" "$title" \
        "${NC:-}${GRAY:-}" "${GRAY:-}" "$(_ui_repeat "$dash" "$rest")" "${NC:-}"
}

# ui_phase_begin "NAME" [TOTAL] — start a phase; resets the step counter.
ui_phase_begin() {
    UI_PHASE_NAME="${1:-}"
    UI_PHASE_TOTAL="${2:-0}"
    UI_STEP=0
    echo
    ui_rule "$UI_PHASE_NAME"
}

_ui_step_tag() {
    if [ "${UI_PHASE_TOTAL:-0}" -gt 0 ] 2>/dev/null; then
        printf '[%02d/%02d]' "${UI_STEP:-0}" "$UI_PHASE_TOTAL"
    else
        printf '[%02d]' "${UI_STEP:-0}"
    fi
}

_ui_pad() {  # _ui_pad <string> <width>
    local s="$1" width="$2" n=${#1}
    if [ "$n" -ge "$width" ]; then printf '%s' "$s"; else printf '%s%*s' "$s" $((width - n)) ''; fi
}

_ui_line_count() {
    [ -f "$1" ] && wc -l < "$1" 2>/dev/null | tr -d ' ' || printf '0'
}

_ui_mark_complete() {
    [ -n "${OUTDIR:-}" ] || return 0
    mkdir -p "$OUTDIR/reports" 2>/dev/null || true
    printf '%s\n' "$1" >> "$OUTDIR/reports/.completed" 2>/dev/null || true
}

# _ui_result_row <kind> <name> <lines> — one aligned outcome line.
_ui_result_row() {
    local kind="$1" name="$2" lines="$3" glyph color detail
    case "$kind" in
        ok)      glyph="${UI_OK:-+}";      color="${GREEN:-}";  detail="${lines} lines" ;;
        fail)    glyph="${UI_BAD:-x}";     color="${RED:-}";    detail="no data" ;;
        timeout) glyph="${UI_TIMEOUT:-~}"; color="${YELLOW:-}"; detail="timeout" ;;
        stop)    glyph="${UI_STOP:-!}";    color="${ORANGE:-}"; detail="stopped" ;;
        skip)    glyph="${UI_OK:-+}";      color="${GRAY:-}";   detail="cached (${lines} lines)" ;;
        *)       glyph='?';                color="${GRAY:-}";   detail="$lines" ;;
    esac
    printf '  %b%s%b  %s %b%s%b\n' "$color" "$glyph" "${NC:-}" "$(_ui_pad "$name" 34)" "${DIM:-}" "$detail" "${NC:-}"
}

# ---- The scan runner --------------------------------------------------------
# execute_scan <name> <command> <timeout> <output> [critical=false]
# Signature preserved so the ~30 existing call sites need no changes.
execute_scan() {
    local name="$1" command="$2" timeout_s="$3" output="$4" critical="${5:-false}"
    local parallel="${UI_PARALLEL:-0}" tag=''

    CURRENT_SCAN="$name"
    if [ "$parallel" != 1 ]; then
        UI_STEP=$(( ${UI_STEP:-0} + 1 ))
        tag="$(_ui_step_tag)"
    fi
    command -v log_info >/dev/null 2>&1 && log_info "Starting scan: $name (timeout: ${timeout_s}s)"
    mkdir -p "$(dirname "$output")" 2>/dev/null || true

    # --resume: skip a step whose output already exists and is non-empty.
    if [ "${UI_RESUME:-0}" = 1 ] && [ -s "$output" ]; then
        [ -n "$tag" ] && printf '%b%s%b ' "${GRAY:-}" "$tag" "${NC:-}"
        _ui_result_row skip "$name" "$(_ui_line_count "$output")"
        CURRENT_SCAN=""
        return 0
    fi

    # Non-TTY or inside a parallel group: no spinner, no carriage returns —
    # just atomic start/result lines that are safe to interleave.
    if [ "${UI_TTY:-0}" -ne 1 ] || [ "$parallel" = 1 ]; then
        if [ "$parallel" = 1 ]; then
            printf '  %b%s%b %s\n' "${CYAN:-}" "${UI_RUN:->}" "${NC:-}" "$name"
        else
            printf '%b%s%b %b%s%b %b(timeout %ss)%b\n' \
                "${ORANGE:-}" "$tag" "${NC:-}" "${WHITE:-}" "$name" "${NC:-}" \
                "${DIM:-}" "$timeout_s" "${NC:-}"
        fi
        local rc=0
        if [ "${SCAN_INTERRUPTED:-false}" = true ]; then
            rc=130
        else
            timeout "$timeout_s" bash -c "$command" > "$output" 2>&1 || rc=$?
        fi
        _ui_finish_row "$rc" "$name" "$output" "$critical"
        return $?
    fi

    # TTY single-task: smooth spinner tied to the real command pid (10 fps),
    # real elapsed from $SECONDS.
    printf '%b%s%b %b%s%b %b(timeout %ss)%b\n' \
        "${ORANGE:-}" "$tag" "${NC:-}" "${WHITE:-}" "$name" "${NC:-}" \
        "${DIM:-}" "$timeout_s" "${NC:-}"

    ( timeout "$timeout_s" bash -c "$command" > "$output" 2>&1 ) &
    local cmd_pid=$! i=0 start=$SECONDS el
    printf '\033[?25l'                       # hide cursor
    while kill -0 "$cmd_pid" 2>/dev/null; do
        [ "${SCAN_INTERRUPTED:-false}" = true ] && break
        el=$(( SECONDS - start ))
        printf '\r  %b%s%b %s %b%d:%02d%b   ' \
            "${YELLOW:-}" "${UI_FRAMES[$(( i % UI_NFRAMES ))]}" "${NC:-}" \
            "$name" "${DIM:-}" "$((el / 60))" "$((el % 60))" "${NC:-}"
        i=$(( i + 1 ))
        sleep 0.1
    done
    printf '\r\033[K'                         # clear the spinner line
    printf '\033[?25h'                        # restore cursor

    local rc=0
    if [ "${SCAN_INTERRUPTED:-false}" = true ] && kill -0 "$cmd_pid" 2>/dev/null; then
        kill -TERM "$cmd_pid" 2>/dev/null || true
        wait "$cmd_pid" 2>/dev/null || true
        rc=130
    else
        wait "$cmd_pid" || rc=$?
    fi
    _ui_finish_row "$rc" "$name" "$output" "$critical"
    return $?
}

# _ui_finish_row <rc> <name> <output> <critical> — classify + print; return
# non-zero only for a critical step that produced nothing.
_ui_finish_row() {
    local rc="$1" name="$2" output="$3" critical="$4" lines
    CURRENT_SCAN=""
    lines="$(_ui_line_count "$output")"

    if [ "$rc" -eq 130 ] || [ "${SCAN_INTERRUPTED:-false}" = true ]; then
        echo "SCAN INTERRUPTED" >> "$output" 2>/dev/null || true
        _ui_result_row stop "$name" "$lines"
        return 0
    fi
    if [ "$rc" -eq 124 ]; then
        echo "TIMEOUT AFTER ${name} step" >> "$output" 2>/dev/null || true
        _ui_result_row timeout "$name" "$lines"
        command -v log_warn >/dev/null 2>&1 && log_warn "Timeout: $name"
        [ "$critical" = true ] && [ ! -s "$output" ] && return 1
        return 0
    fi
    if [ -s "$output" ]; then
        _ui_result_row ok "$name" "$lines"
        command -v log_info >/dev/null 2>&1 && log_info "Completed: $name ($lines lines)"
        _ui_mark_complete "$name"
        return 0
    fi
    _ui_result_row fail "$name" "$lines"
    command -v log_warn >/dev/null 2>&1 && log_warn "No data: $name"
    [ "$critical" = true ] && return 1
    return 0
}
