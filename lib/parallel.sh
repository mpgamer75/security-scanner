# shellcheck shell=bash
# =============================================================================
# lib/parallel.sh — bounded concurrent job pool.
#
# The scanner previously ran every step strictly sequentially (8-10 back-to-back
# nmap invocations), which is slow and an obvious "scan storm" to an IDS.
# run_parallel runs independent steps concurrently with a cap, shrinking both
# wall-clock time and the burst signature.
# =============================================================================

# _have_wait_n : bash >= 4.3 supports `wait -n` (wait for the next job).
_have_wait_n() {
    [ "${BASH_VERSINFO[0]:-0}" -gt 4 ] ||
        { [ "${BASH_VERSINFO[0]:-0}" -eq 4 ] && [ "${BASH_VERSINFO[1]:-0}" -ge 3 ]; }
}

# run_parallel <max> <cmd> [cmd ...]
# Each <cmd> is a string evaluated in a background subshell. Never runs more
# than <max> at once; returns after all have finished.
run_parallel() {
    local max="${1:-4}"; shift
    [ "$max" -lt 1 ] 2>/dev/null && max=1
    local running=0 cmd
    local waitn=1
    _have_wait_n || waitn=0
    for cmd in "$@"; do
        eval "$cmd" &
        running=$((running + 1))
        if [ "$running" -ge "$max" ]; then
            if [ "$waitn" -eq 1 ]; then
                wait -n 2>/dev/null || wait
                running=$((running - 1))
            else
                wait
                running=0
            fi
        fi
    done
    wait
}

# run_scan_group <name> <cmd> [cmd ...]
# Run a set of independent execute_scan calls concurrently. Inside a group,
# execute_scan (lib/ui.sh) drops its shared-line spinner in favour of atomic
# start/result lines that are safe to interleave. The phase step counter is
# advanced by the group size afterward so subsequent sequential steps stay
# consistent.
run_scan_group() {
    local name="$1"; shift
    local count=$#
    [ "$count" -eq 0 ] && return 0
    local prev="${UI_PARALLEL:-0}"
    printf '  %b%s%b %b(%d parallel tasks, cap %s)%b\n' \
        "${CYAN:-}" "${name}" "${NC:-}" "${DIM:-}" "$count" "${MAX_PARALLEL:-4}" "${NC:-}"
    UI_PARALLEL=1
    run_parallel "${MAX_PARALLEL:-4}" "$@"
    UI_PARALLEL="$prev"
    UI_STEP=$(( ${UI_STEP:-0} + count ))
    return 0
}
