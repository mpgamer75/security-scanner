# shellcheck shell=bash
# =============================================================================
# lib/targeting.sh — target classification, host extraction, and phase planning.
# Pure functions, no side effects on source. Lets the scanner adapt its strategy
# to the target type instead of always assuming a single IP.
# =============================================================================

# _valid_ipv4 <str> : return 0 if str is a dotted quad with each octet 0-255.
_valid_ipv4() {
    local ip="$1" octet
    local IFS=.
    # shellcheck disable=SC2086
    set -- $ip
    [ "$#" -eq 4 ] || return 1
    for octet in "$@"; do
        case "$octet" in
            ''|*[!0-9]*) return 1 ;;
        esac
        [ "$octet" -le 255 ] || return 1
    done
    return 0
}

# profile_target <input> : echo one of url|cidr|ip|ipv6|hostname|unknown
profile_target() {
    local t="$1"
    [ -z "$t" ] && { echo unknown; return; }
    case "$t" in
        *' '*) echo unknown; return ;;
        http://*|https://*) echo url; return ;;
    esac
    # IPv4 CIDR
    if printf '%s' "$t" | grep -qE '^[0-9]{1,3}(\.[0-9]{1,3}){3}/[0-9]{1,2}$'; then
        echo cidr; return
    fi
    # IPv6 CIDR (has a colon and a /prefix)
    if printf '%s' "$t" | grep -qE '^[0-9a-fA-F:]+/[0-9]{1,3}$' && printf '%s' "$t" | grep -q ':'; then
        echo cidr; return
    fi
    # IPv4
    if printf '%s' "$t" | grep -qE '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'; then
        if _valid_ipv4 "$t"; then echo ip; else echo unknown; fi
        return
    fi
    # IPv6
    if printf '%s' "$t" | grep -qE '^[0-9a-fA-F:]+$' && printf '%s' "$t" | grep -q ':'; then
        echo ipv6; return
    fi
    # Hostname (FQDN or single label)
    if printf '%s' "$t" | grep -qiE '^([a-z0-9]([a-z0-9-]*[a-z0-9])?\.)+[a-z]{2,}$'; then
        echo hostname; return
    fi
    if printf '%s' "$t" | grep -qiE '^[a-z0-9]([a-z0-9-]*[a-z0-9])?$'; then
        echo hostname; return
    fi
    echo unknown
}

# target_host <input> : strip scheme / path / userinfo / port -> bare host.
target_host() {
    local t="$1"
    t="${t#http://}"
    t="${t#https://}"
    t="${t%%/*}"     # drop path
    t="${t##*@}"     # drop userinfo
    case "$t" in
        \[*\]*) t="${t#\[}"; t="${t%%\]*}" ;;   # [ipv6]:port
        *:*:*) : ;;                              # bare ipv6, keep
        *:*) t="${t%%:*}" ;;                     # host:port
    esac
    printf '%s' "$t"
}

# target_plan <type> : echo the space-separated recon phases best suited to a
# target type. Used to adapt which phases run and in what emphasis.
target_plan() {
    case "$1" in
        url)      echo "web network" ;;
        cidr)     echo "network" ;;
        ip|ipv6)  echo "network web" ;;
        hostname) echo "osint network web" ;;
        *)        echo "osint network web" ;;
    esac
}
