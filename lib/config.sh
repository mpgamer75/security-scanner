# shellcheck shell=bash
# =============================================================================
# lib/config.sh — secure API-key storage and accessors.
#
# Keys live in ${XDG_CONFIG_HOME:-~/.config}/security-scanner/config.env, a
# shell-sourceable file created 0600 in a 0700 directory. Integrations are
# opt-in: a missing key means the enricher cleanly skips. Nothing here is ever
# committed (config dir is outside the repo and *.env is gitignored).
# =============================================================================

CONFIG_KNOWN_KEYS="SHODAN_API_KEY CENSYS_API_ID CENSYS_API_SECRET HUNTER_API_KEY VIRUSTOTAL_API_KEY SECURITYTRAILS_API_KEY"

config_dir() {
    if [ -n "${SECURITY_SCANNER_CONFIG_DIR:-}" ]; then
        printf '%s' "$SECURITY_SCANNER_CONFIG_DIR"; return
    fi
    local base="${XDG_CONFIG_HOME:-$HOME/.config}"
    # Under sudo, prefer the invoking user's config so keys set as the user are
    # still found when the scan itself runs as root (sudo nmap -sS/-O/-sU).
    if [ "$(id -u 2>/dev/null || echo 1000)" = "0" ] && [ -n "${SUDO_USER:-}" ]; then
        local home
        home="$(getent passwd "$SUDO_USER" 2>/dev/null | cut -d: -f6)"
        [ -n "$home" ] && base="$home/.config"
    fi
    printf '%s/security-scanner' "$base"
}

config_file() {
    printf '%s/config.env' "$(config_dir)"
}

# load_config — source the config file (exporting its keys) if present. Warns
# when the file is more permissive than 0600.
load_config() {
    local f; f="$(config_file)"
    [ -f "$f" ] || return 0
    local mode=''
    if command -v stat >/dev/null 2>&1; then
        mode="$(stat -c '%a' "$f" 2>/dev/null || stat -f '%Lp' "$f" 2>/dev/null || echo '')"
    fi
    case "$mode" in
        ''|600|400) ;;
        *) printf '%b[WARN]%b %s is mode %s (expected 600). Run: chmod 600 %s\n' \
                 "${YELLOW:-}" "${NC:-}" "$f" "$mode" "$f" >&2 ;;
    esac
    set -a
    # shellcheck disable=SC1090
    . "$f"
    set +a
    return 0
}

# get_key NAME — echo the value of a loaded key (empty if unset).
get_key() {
    local name="$1"
    printf '%s' "${!name:-}"
}

config_is_known() {
    case " $CONFIG_KNOWN_KEYS " in
        *" $1 "*) return 0 ;;
        *) return 1 ;;
    esac
}

# mask_key VALUE — a non-revealing preview for `config list`.
mask_key() {
    local v="$1" n=${#1}
    if [ "$n" -le 4 ]; then printf '****'; else printf '%s…%s' "${v:0:2}" "${v: -2}"; fi
}

# set_key NAME VALUE — upsert one key, keeping the file 0600 in a 0700 dir.
set_key() {
    local name="$1" value="$2" dir file tmp
    dir="$(config_dir)"; file="$(config_file)"
    mkdir -p "$dir" 2>/dev/null || { printf 'cannot create %s\n' "$dir" >&2; return 1; }
    chmod 700 "$dir" 2>/dev/null || true
    tmp="$(mktemp "${dir}/.cfg.XXXXXX" 2>/dev/null || printf '%s.tmp' "$file")"
    if [ -f "$file" ]; then
        grep -v -E "^[[:space:]]*${name}=" "$file" 2>/dev/null > "$tmp" || true
    fi
    printf '%s=%s\n' "$name" "$value" >> "$tmp"
    mv "$tmp" "$file"
    chmod 600 "$file" 2>/dev/null || true
    return 0
}

# config_cmd <sub> [args...] — the `security config` subcommand.
config_cmd() {
    local sub="${1:-list}"
    shift 2>/dev/null || true
    case "$sub" in
        path)
            config_file; echo ;;
        list)
            load_config
            printf 'Config file: %s\n' "$(config_file)"
            [ -f "$(config_file)" ] || printf '  (not created yet — add a key with: security config set NAME VALUE)\n'
            local k v
            for k in $CONFIG_KNOWN_KEYS; do
                v="${!k:-}"
                if [ -n "$v" ]; then printf '  %-24s set    %s\n' "$k" "$(mask_key "$v")"
                else printf '  %-24s unset\n' "$k"; fi
            done ;;
        get)
            local name="${1:-}"
            [ -z "$name" ] && { printf 'usage: security config get NAME\n' >&2; return 1; }
            load_config; printf '%s\n' "${!name:-}" ;;
        set)
            local name="${1:-}" value="${2:-}"
            [ -z "$name" ] && { printf 'usage: security config set NAME [VALUE]\n' >&2; return 1; }
            config_is_known "$name" || printf 'note: "%s" is not a recognized key (stored anyway)\n' "$name"
            if [ -z "$value" ]; then
                read -rsp "Value for $name (hidden): " value; echo
            fi
            [ -z "$value" ] && { printf 'no value given; nothing changed\n' >&2; return 1; }
            set_key "$name" "$value" && printf 'saved %s to %s\n' "$name" "$(config_file)" ;;
        *)
            printf 'usage: security config {list|set NAME [VALUE]|get NAME|path}\n' >&2
            return 1 ;;
    esac
}
