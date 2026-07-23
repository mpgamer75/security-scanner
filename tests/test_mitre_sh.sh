#!/usr/bin/env bash
# Unit tests for lib/mitre.sh (ATT&CK technique lookup for guidance).
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=tests/helpers.sh
source "$DIR/helpers.sh"
# shellcheck source=lib/mitre.sh
source "$DIR/../lib/mitre.sh"

echo "mitre:"

# technique metadata "TACTIC|Name"
assert_contains "$(mitre_technique_meta T1190)" "TA0001"                "meta-tactic"
assert_contains "$(mitre_technique_meta T1190)" "Exploit Public-Facing" "meta-name"
assert_eq ""    "$(mitre_technique_meta T9999)"                         "meta-unknown"

# service -> indicated Initial Access technique
assert_eq T1110 "$(mitre_service_technique ssh)"           "svc-ssh"
assert_eq T1110 "$(mitre_service_technique ftp)"           "svc-ftp"
assert_eq T1210 "$(mitre_service_technique microsoft-ds)"  "svc-smb"
assert_eq T1210 "$(mitre_service_technique mysql)"         "svc-mysql"
assert_eq T1190 "$(mitre_service_technique http)"          "svc-http"
assert_eq T1190 "$(mitre_service_technique https)"         "svc-https"
assert_eq ""    "$(mitre_service_technique bananas)"       "svc-unknown"

finish
