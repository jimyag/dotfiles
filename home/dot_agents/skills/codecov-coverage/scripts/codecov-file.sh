#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/_common.sh"

usage() {
    cat <<'EOF'
用法: codecov-file.sh <FILE_PATH> [--owner OWNER] [--repo REPO] [--ref REF] [--json]

说明: 获取单个文件的逐行覆盖率数据。
EOF
}

main() {
    show_help_if_requested "$@"
    require_cmd npx
    require_cmd jq
    check_token

    local file_path=""
    local ref=""
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
            --ref)
                shift
                ref="${1:?--ref 需要一个参数}"
                shift
                ;;
            --owner|--repo)
                owner_repo_args+=("$1")
                shift
                owner_repo_args+=("${1:?${owner_repo_args[-1]} 需要一个参数}")
                shift
                ;;
            *)
                if [[ -z "$file_path" ]]; then
                    file_path="$1"
                    shift
                else
                    die "未知参数: $1"
                fi
                ;;
        esac
    done

    [[ -n "$file_path" ]] || die "请指定文件路径，例如: codecov-file.sh src/index.ts"
    parse_owner_repo "${owner_repo_args[@]}"

    local -a extra_args=("file_path:$file_path")
    [[ -n "$ref" ]] && extra_args+=("ref:$ref")

    local result
    result="$(call_codecov get_file_coverage "${extra_args[@]}")"

    if [[ "$json_output" == true ]]; then
        echo "$result" | jq .
    else
        echo "$result" | jq -r '
            "文件: \(.name // "unknown")",
            "覆盖率: \(.totals.coverage // "unknown")%",
            "总行数: \(.totals.lines // 0)",
            "覆盖行: \(.totals.hits // 0)",
            "未覆盖: \(.totals.misses // 0)",
            "",
            "=== 逐行覆盖 ===",
            ((.coverage // {}) | to_entries[] | "L\(.key): " + if .value > 0 then "covered (\(.value)x)" else "missed" end)
        '
    fi
}

main "$@"
