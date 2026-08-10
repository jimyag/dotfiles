#!/usr/bin/env bash

set -euo pipefail

die() {
    echo "错误: $*" >&2
    exit 1
}

require_cmd() {
    command -v "$1" >/dev/null 2>&1 || die "缺少依赖: $1"
}

show_help_if_requested() {
    for arg in "$@"; do
        case "$arg" in
            -h|--help)
                usage
                exit 0
                ;;
        esac
    done
}

check_token() {
    [[ -n "${CODECOV_TOKEN:-}" ]] || die "CODECOV_TOKEN 未设置。请执行: export CODECOV_TOKEN='your-api-access-token'"
}

parse_owner_repo() {
    OWNER=""
    REPO=""
    REMAINING_ARGS=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            --owner)
                shift
                OWNER="${1:?--owner 需要一个参数}"
                ;;
            --repo)
                shift
                REPO="${1:?--repo 需要一个参数}"
                ;;
            *)
                REMAINING_ARGS+=("$1")
                ;;
        esac
        shift
    done

    if [[ -z "$OWNER" || -z "$REPO" ]]; then
        local remote_url
        remote_url="$(git remote get-url origin 2>/dev/null || true)"
        if [[ "$remote_url" =~ github\.com[:/]([^/]+)/([^/.]+)(\.git)?$ ]]; then
            [[ -z "$OWNER" ]] && OWNER="$(echo "$remote_url" | sed -E 's|.*github\.com[:/]([^/]+)/([^/.]+).*|\1|')"
            [[ -z "$REPO" ]] && REPO="$(echo "$remote_url" | sed -E 's|.*github\.com[:/]([^/]+)/([^/.]+).*|\2|')"
        fi
    fi

    [[ -n "$OWNER" ]] || die "无法检测 owner，请使用 --owner 指定"
    [[ -n "$REPO" ]] || die "无法检测 repo，请使用 --repo 指定"
}

call_codecov() {
    local tool="$1"
    shift

    npx -y mcporter call \
        --stdio "npx -y @egulatee/mcp-codecov" \
        --env CODECOV_TOKEN="$CODECOV_TOKEN" \
        --name codecov \
        "$tool" \
        "owner:$OWNER" "repo:$REPO" \
        "$@"
}
