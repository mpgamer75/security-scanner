# shellcheck shell=bash
# Minimal assertion helpers for the bash unit tests (no bats dependency).

TESTS_RUN=0
TESTS_FAIL=0

assert_eq() {
    local expected="$1" actual="$2" msg="${3:-assert_eq}"
    TESTS_RUN=$((TESTS_RUN + 1))
    if [ "$expected" != "$actual" ]; then
        TESTS_FAIL=$((TESTS_FAIL + 1))
        echo "  FAIL: $msg — expected [$expected] got [$actual]"
    fi
}

assert_contains() {
    local haystack="$1" needle="$2" msg="${3:-assert_contains}"
    TESTS_RUN=$((TESTS_RUN + 1))
    case "$haystack" in
        *"$needle"*) ;;
        *) TESTS_FAIL=$((TESTS_FAIL + 1)); echo "  FAIL: $msg — [$needle] not in [$haystack]" ;;
    esac
}

assert_not_contains() {
    local haystack="$1" needle="$2" msg="${3:-assert_not_contains}"
    TESTS_RUN=$((TESTS_RUN + 1))
    case "$haystack" in
        *"$needle"*) TESTS_FAIL=$((TESTS_FAIL + 1)); echo "  FAIL: $msg — [$needle] unexpectedly in [$haystack]" ;;
        *) ;;
    esac
}

finish() {
    echo "  ran $TESTS_RUN assertions, $TESTS_FAIL failed"
    [ "$TESTS_FAIL" -eq 0 ]
}
