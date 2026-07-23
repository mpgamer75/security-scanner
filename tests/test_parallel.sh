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
finish
