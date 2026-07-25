#!/usr/bin/env bash
# Unit tests for lib/parallel.sh (bounded concurrent job pool).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"
# shellcheck source=lib/parallel.sh
source "$DIR/../lib/parallel.sh"

echo "parallel:"

WORK="$(mktemp -d)"
echo 0 > "$WORK/cur"
echo 0 > "$WORK/peak"

# A job records peak concurrency via a mkdir-based lock, then leaves a marker.
job() {
    local id="$1"
    while ! mkdir "$WORK/lock" 2>/dev/null; do :; done
    local c=$(( $(cat "$WORK/cur") + 1 )); echo "$c" > "$WORK/cur"
    [ "$c" -gt "$(cat "$WORK/peak")" ] && echo "$c" > "$WORK/peak"
    rmdir "$WORK/lock"
    sleep 0.2
    while ! mkdir "$WORK/lock" 2>/dev/null; do :; done
    echo $(( $(cat "$WORK/cur") - 1 )) > "$WORK/cur"
    rmdir "$WORK/lock"
    : > "$WORK/marker.$id"
}

cmds=()
for i in 1 2 3 4 5 6; do cmds+=("job $i"); done
run_parallel 2 "${cmds[@]}"

markers=$(find "$WORK" -name 'marker.*' | wc -l | tr -d ' ')
assert_eq 6 "$markers" "all-6-jobs-ran"

peak=$(cat "$WORK/peak")
# Core invariant: the pool never exceeds max concurrency (a broken pool would
# run all 6 at once -> peak 6). peak must be >=1 and <= max (2).
assert_eq yes "$([ "$peak" -ge 1 ] && [ "$peak" -le 2 ] && echo yes || echo no)" "peak-bounded (peak=$peak)"

rm -rf "$WORK"

# --- run_scan_group ---------------------------------------------------------
# Runs every task, sets/restores UI_PARALLEL, and advances the step counter by
# the group size so subsequent sequential steps stay consistent.
UI_STEP=5; UI_PARALLEL=0; MAX_PARALLEL=4
G="$(mktemp -d)"
grp_task() { : > "$G/task.$1"; }
run_scan_group "grp" "grp_task a" "grp_task b" "grp_task c" >/dev/null 2>&1
gcount=$(find "$G" -name 'task.*' | wc -l | tr -d ' ')
assert_eq 3 "$gcount" "run_scan_group ran all tasks"
assert_eq 8 "$UI_STEP" "run_scan_group advanced UI_STEP by group size"
assert_eq 0 "$UI_PARALLEL" "run_scan_group restored UI_PARALLEL"
rm -rf "$G"

finish
