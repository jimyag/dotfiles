#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

usage() {
    cat <<'EOF'
用法: codecov-pr.sh <PR_NUMBER> [--owner OWNER] [--repo REPO] [--json]

说明: 获取 PR 的覆盖率影响，包括 base/head/patch 覆盖率。
EOF
}

main() {
    show_help_if_requested "$@"
    require_cmd npx
    require_cmd jq
    check_token

    local pr_number=""
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
                if [[ -z "$pr_number" && "$1" =~ ^[0-9]+$ ]]; then
                    pr_number="$1"
                    shift
                else
                    die "未知参数: $1"
                fi
                ;;
        esac
    done

    [[ -n "$pr_number" ]] || die "请指定 PR 号，例如: codecov-pr.sh 123"
    parse_owner_repo "${owner_repo_args[@]}"

    local result
    result="$(call_codecov get_pull_request_coverage "pull_number:$pr_number")"

    if [[ "$json_output" == true ]]; then
        echo "$result" | jq .
    else
        echo "$result" | jq -r '
            "PR #\(.pullid // "unknown"): \(.title // "unknown")",
            "",
            "Base 覆盖率: \(.base_totals.coverage // "unknown")%",
            "Head 覆盖率: \(.head_totals.coverage // "unknown")%",
            "Patch 覆盖率: \(.patch_totals.coverage // "unknown")%",
            "",
            "Base 文件数: \(.base_totals.files // 0)",
            "Head 文件数: \(.head_totals.files // 0)",
            "Patch 文件数: \(.patch_totals.files // 0)",
            "Patch 总行数: \(.patch_totals.lines // 0)",
            "Patch 覆盖行: \(.patch_totals.hits // 0)",
            "Patch 未覆盖: \(.patch_totals.misses // 0)"
        '
    fi
}

main "$@"
