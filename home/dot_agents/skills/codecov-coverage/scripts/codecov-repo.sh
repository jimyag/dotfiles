#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

usage() {
    cat <<'EOF'
用法: codecov-repo.sh [--owner OWNER] [--repo REPO] [--branch BRANCH] [--json]

说明: 获取仓库整体覆盖率统计。owner/repo 默认从 git remote 自动检测。
EOF
}

main() {
    show_help_if_requested "$@"
    require_cmd npx
    require_cmd jq
    check_token

    local branch=""
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
            --branch)
                shift
                branch="${1:?--branch 需要一个参数}"
                shift
                ;;
            --owner|--repo)
                owner_repo_args+=("$1")
                shift
                owner_repo_args+=("${1:?${owner_repo_args[-1]} 需要一个参数}")
                shift
                ;;
            *)
                die "未知参数: $1"
                ;;
        esac
    done

    parse_owner_repo "${owner_repo_args[@]}"

    local -a extra_args=()
    [[ -n "$branch" ]] && extra_args+=("branch:$branch")

    local result
    result="$(call_codecov get_repo_coverage "${extra_args[@]}")"

    if [[ "$json_output" == true ]]; then
        echo "$result" | jq .
    else
        echo "$result" | jq -r '
            "仓库: \(.author.name // "unknown")/\(.name // "unknown")",
            "分支: \(.branch // "unknown")",
            "语言: \(.language // "unknown")",
            "状态: \(if .active then "活跃" else "未活跃" end)",
            "",
            "覆盖率: \(.totals.coverage // "unknown")%",
            "文件数: \(.totals.files // 0)",
            "总行数: \(.totals.lines // 0)",
            "覆盖行: \(.totals.hits // 0)",
            "未覆盖: \(.totals.misses // 0)",
            "部分覆盖: \(.totals.partials // 0)",
            "",
            "更新时间: \(.updatestamp // "unknown")"
        '
    fi
}

main "$@"
