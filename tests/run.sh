#!/usr/bin/env bash
# Run the whole test suite: bash lib unit tests + python report unit tests.
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
fail=0

echo "== bash unit tests =="
for t in "$DIR"/test_*.sh; do
    echo "- $(basename "$t")"
    bash "$t" || fail=1
done

echo ""
echo "== python unit tests =="
if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
( cd "$ROOT" && "$PY" -m unittest discover -s report/tests -p "test_*.py" ) || fail=1

echo ""
if [ "$fail" -eq 0 ]; then echo "ALL TESTS PASSED"; else echo "SOME TESTS FAILED"; fi
exit $fail
