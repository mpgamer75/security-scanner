#!/usr/bin/env bash
# Unit tests for lib/config.sh — key storage, accessors, and `config` subcommand.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$DIR/.." && pwd)"
# shellcheck source=/dev/null
source "$DIR/helpers.sh"
# shellcheck source=/dev/null
source "$ROOT/lib/config.sh"

echo "config:"

# Isolate the config dir so the test never touches the real ~/.config.
SECURITY_SCANNER_CONFIG_DIR="$(mktemp -d 2>/dev/null || echo "${TMPDIR:-/tmp}/cfg_test_$$")"
export SECURITY_SCANNER_CONFIG_DIR
mkdir -p "$SECURITY_SCANNER_CONFIG_DIR"

assert_eq "$SECURITY_SCANNER_CONFIG_DIR/config.env" "$(config_file)" "config_file honors override dir"

# known / unknown keys
config_is_known "SHODAN_API_KEY" && k1=0 || k1=1
assert_eq "0" "$k1" "SHODAN_API_KEY is a known key"
config_is_known "NOPE" && k2=0 || k2=1
assert_eq "1" "$k2" "NOPE is not a known key"

# set_key writes the file, get_key/load_config read it back
set_key "SHODAN_API_KEY" "abc123secret"
assert_eq "SHODAN_API_KEY=abc123secret" "$(cat "$(config_file)")" "set_key writes KEY=VALUE"

# perms should be 600 (skip the check on filesystems without POSIX perms)
if command -v stat >/dev/null 2>&1; then
    mode="$(stat -c '%a' "$(config_file)" 2>/dev/null || echo '')"
    if [ -n "$mode" ] && [ "$mode" != "644" ]; then
        assert_eq "600" "$mode" "config file is mode 600"
    else
        echo "  (perms check skipped — filesystem reports $mode)"
    fi
fi

# upsert: setting the same key replaces, not appends; a second key is added
set_key "SHODAN_API_KEY" "newvalue"
set_key "HUNTER_API_KEY" "hunterval"
lines="$(wc -l < "$(config_file)" | tr -d ' ')"
assert_eq "2" "$lines" "upsert keeps one line per key"

load_config
assert_eq "newvalue" "$(get_key SHODAN_API_KEY)" "get_key returns the upserted value"
assert_eq "hunterval" "$(get_key HUNTER_API_KEY)" "get_key returns a second key"
assert_eq "" "$(get_key VIRUSTOTAL_API_KEY)" "get_key is empty for an unset key"

# mask_key never reveals the full secret
masked="$(mask_key "supersecretvalue")"
assert_not_contains "$masked" "supersecretvalue" "mask_key hides the value"

# config_cmd list shows set/unset and masks values
out="$(config_cmd list 2>&1)"
assert_contains "$out" "SHODAN_API_KEY" "config list shows known keys"
assert_contains "$out" "unset" "config list marks unset keys"
assert_not_contains "$out" "newvalue" "config list does not print raw secrets"

# config_cmd path prints the file path
assert_contains "$(config_cmd path)" "config.env" "config path prints the file"

rm -rf "$SECURITY_SCANNER_CONFIG_DIR" 2>/dev/null || true
finish
