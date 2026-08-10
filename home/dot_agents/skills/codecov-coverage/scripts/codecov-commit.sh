#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

usage() {
    cat <<'EOF'
用法: codecov-commit.sh [SHA] [--owner OWNER] [--repo REPO] [--json]

说明: 获取某个 commit 的覆盖率详情。不传 SHA 时使用当前 HEAD。
EOF
}

main() {
    show_help_if_requested "$@"
    require_cmd npx
    require_cmd jq
    require_cmd git
    check_token

    local sha=""
    local json_output=false
    local -a owner_repo_args=()

    while [[ $# -gt 0 ]]; do
        case "$1" in
            -h|--help)
                usage
                exit 0
                ;;
            --json)
                json_output=true
                shift
                ;;
            --owner|--repo)
                owner_repo_args+=("$1")
                shift
                owner_repo_args+=("${1:?${owner_repo_args[-1]} 需要一个参数}")
                shift
                ;;
            *)
                if [[ -z "$sha" ]]; then
                    sha="$1"
                    shift
                else
                    die "未知参数: $1"
                fi
                ;;
        esac
    done

    parse_owner_repo "${owner_repo_args[@]}"

    if [[ -z "$sha" ]]; then
        sha="$(git rev-parse HEAD 2>/dev/null || die "无法获取当前 HEAD")"
    fi

    [[ "$sha" =~ ^[0-9a-f]{7,40}$ ]] || die "无效的 commit SHA: $sha"

    local result
    result="$(call_codecov get_commit_coverage "commit_sha:$sha")"

    if [[ "$json_output" == true ]]; then
        echo "$result" | jq '{commitid, message, branch, author, timestamp, ci_passed, totals, state}'
    else
        echo "$result" | jq -r '
            "Commit: \(.commitid // "unknown")",
            "消息: \((.message // "unknown") | split("\n")[0])",
            "分支: \(.branch // "unknown")",
            "作者: \(.author.name // "unknown")",
            "时间: \(.timestamp // "unknown")",
            "CI: \(if .ci_passed then "通过" else "未通过" end)",
            "",
            "覆盖率: \(.totals.coverage // "unknown")%",
            "文件数: \(.totals.files // 0)",
            "总行数: \(.totals.lines // 0)",
            "覆盖行: \(.totals.hits // 0)",
            "未覆盖: \(.totals.misses // 0)",
            "部分覆盖: \(.totals.partials // 0)"
        '
    fi
}

main "$@"
