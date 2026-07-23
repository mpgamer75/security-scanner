#!/usr/bin/env bash
# Unit tests for lib/targeting.sh (target classification + host extraction).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"
# shellcheck source=lib/targeting.sh
source "$DIR/../lib/targeting.sh"

echo "targeting:"

# profile_target classification
assert_eq ip       "$(profile_target 10.0.0.5)"                  "ipv4"
assert_eq ip       "$(profile_target 192.168.1.100)"             "ipv4-b"
assert_eq cidr     "$(profile_target 192.168.0.0/24)"            "cidr"
assert_eq url      "$(profile_target https://example.com/a)"     "url"
assert_eq url      "$(profile_target http://10.0.0.5:8080)"      "url-with-port"
assert_eq hostname "$(profile_target example.com)"               "hostname"
assert_eq hostname "$(profile_target sub.example.co.uk)"         "hostname-multi"
assert_eq ipv6     "$(profile_target 2001:db8::1)"               "ipv6"
assert_eq cidr     "$(profile_target fe80::/10)"                 "ipv6-cidr"
assert_eq unknown  "$(profile_target '')"                        "empty"
assert_eq unknown  "$(profile_target 'has space')"               "space"
assert_eq unknown  "$(profile_target 999.1.1.1)"                 "bad-octet"

# target_host extraction (bare host for scanning)
assert_eq example.com "$(target_host https://example.com/path?x=1)" "th-url"
assert_eq 10.0.0.5    "$(target_host http://10.0.0.5:8080/a)"       "th-url-port"
assert_eq 10.0.0.5    "$(target_host 10.0.0.5)"                     "th-ip"
assert_eq example.com "$(target_host example.com)"                  "th-host"

# recommended phase plan per target type (web-first for url, discovery for cidr)
assert_contains "$(target_plan url)"      web     "plan-url-web"
assert_contains "$(target_plan cidr)"     network "plan-cidr-net"
assert_contains "$(target_plan hostname)" osint   "plan-host-osint"

finish
