#!/bin/bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT

zsh -f -ic '
    set -e
    autoload -Uz compinit
    compinit -d "$2/zcompdump"
    source "$1/home/dot_profile.d/common"
    [[ "$(bindkey "^R")" == *fzf-history-widget* ]]
    [[ "$(bindkey "^T")" == *fzf-file-widget* ]]
    (( $+functions[_fzf_complete] ))
    source "$1/home/dot_profile.d/alias"
    [[ "${aliases[ll]}" == eza* && "${aliases[lt]}" == eza* ]]
    [[ "${aliases[cat]:-}" != bat* && "${aliases[ls]:-}" != eza* ]]
    source "$1/home/dot_profile.d/function"
    mkdir -p "$2/target with spaces"
    export TMPDIR="$2"
    yazi() {
        local argument
        for argument in "$@"; do
            if [[ "$argument" == --cwd-file=* ]]; then
                print -r -- "$TEST_CWD" > "${argument#--cwd-file=}"
            fi
        done
        return "${TEST_RESULT:-0}"
    }
    TEST_CWD="$2/target with spaces"
    y
    [[ "$PWD" == "$TEST_CWD" ]]
    TEST_CWD="$2/missing"
    if y; then exit 1; fi
    [[ "$PWD" == "$2/target with spaces" ]]
    TEST_RESULT=7
    if y; then exit 1; else [[ "$?" == 7 ]]; fi
    [[ "$PWD" == "$2/target with spaces" ]]
    TEST_RESULT=0 TEST_CWD=""
    y
    [[ "$PWD" == "$2/target with spaces" ]]
    setopt nullglob
    leftovers=("$2"/yazi-cwd.*)
    (( ${#leftovers} == 0 ))
' -- "$repo_root" "$tmpdir"

echo 'Terminal tools checks passed'
