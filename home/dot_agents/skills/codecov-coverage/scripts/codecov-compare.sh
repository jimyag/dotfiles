#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

usage() {
    cat <<'EOF'
用法: codecov-compare.sh <BASE> <HEAD> [--owner OWNER] [--repo REPO] [--json]

说明: 比较两个 git 引用（分支、commit、tag）之间的覆盖率差异。
EOF
}

main() {
    show_help_if_requested "$@"
    require_cmd npx
    require_cmd jq
    check_token

    local json_output=false
    local -a owner_repo_args=()
    local -a refs=()

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
                refs+=("$1")
                shift
                ;;
        esac
    done

    [[ ${#refs[@]} -ge 2 ]] || die "请指定 base 和 head，例如: codecov-compare.sh main feature"
    parse_owner_repo "${owner_repo_args[@]}"

    local result
    result="$(call_codecov compare_coverage "base:${refs[0]}" "head:${refs[1]}")"

    if [[ "$json_output" == true ]]; then
        echo "$result" | jq .
    else
        echo "$result" | jq -r '
            "比较: \((.base_commit // "unknown")[:8]) -> \((.head_commit // "unknown")[:8])",
            "",
            "=== 总体覆盖率 ===",
            "Base: \(.totals.base.coverage // "unknown")% (\(.totals.base.files // 0) 文件, \(.totals.base.lines // 0) 行)",
            "Head: \(.totals.head.coverage // "unknown")% (\(.totals.head.files // 0) 文件, \(.totals.head.lines // 0) 行)",
            "Patch: \(.totals.patch.coverage // "unknown")% (\(.totals.patch.files // 0) 文件, \(.totals.patch.lines // 0) 行)",
            "",
            "=== 变化文件 (\((.files // []) | length) 个) ===",
            ((.files // [])[:20][] | "\(.name.head // .name.base // "unknown"): base=\((.totals.base.coverage // 0))% head=\((.totals.head.coverage // 0))% patch=\((.totals.patch.coverage // 0))%"),
            if ((.files // []) | length) > 20 then "... 还有 \(((.files // []) | length) - 20) 个文件" else "" end
        '
    fi
}

main "$@"
