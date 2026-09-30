#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")/.."
zsh <<'ZSH'
source home/dot_profile.d/git-worktree-helper

function git() {
    case "$*" in
        'remote get-url upstream')
            [[ "$scenario" == upstream ]] || return 2
            print 'git@github.com:team/project.git' ;;
        'remote get-url origin') print 'git@github.com:me/project.git' ;;
        'worktree list'*)
            print 'worktree /tmp/project'
            print 'branch refs/heads/main'
            print 'worktree /tmp/project-feature'
            print "branch refs/heads/$branch" ;;
        *) return 1 ;;
    esac
}

function gh() {
    case "$1 $2" in
        'repo view')
            [[ "$scenario" != upstream ]] || return 1
            print 'team/project' ;;
        'pr list')
            [[ "$scenario" != failure ]] || { print -u2 'API unavailable'; return 1; }
            if [[ "$scenario" == missing || "$scenario" == branch-issue || "$*" == *'--repo me/project'* && "$scenario" != origin ]]; then
                print '[]'
            else
                print '[{"headRefName":"feature","number":12,"title":"Feature PR","state":"MERGED","closingIssuesReferences":[{"number":7,"title":"First issue"},{"number":8,"title":"Second issue"}]}]'
            fi ;;
        'issue view')
            [[ "$2 $3" == 'view 42' ]] || return 1
            print '#42 Branch issue' ;;
        *) return 1 ;;
    esac
}

for scenario in parent upstream origin missing failure branch-issue; do
    branch=feature
    [[ "$scenario" == branch-issue ]] && branch=issue-42
    # Merge stderr so warning behavior is checked without temporary files.
    output=$(gwl 2>&1) || exit 1
    case "$scenario" in
        parent|upstream|origin)
            [[ "$output" == *'[M] #12 Feature PR'* && "$output" == *'#7 First issue; #8 Second issue'* && "$output" != *'未找到匹配 PR'* ]] || { print -u2 "$scenario: $output"; exit 1; } ;;
        missing)
            [[ "$output" == *'分支 feature 未找到匹配 PR'* && "$output" == *'me/project team/project'* ]] || exit 1 ;;
        failure)
            [[ "$output" == *'API unavailable'* && "$output" == *'查询 me/project 的 PR 失败'* ]] || exit 1 ;;
        branch-issue)
            [[ "$output" == *'#42 Branch issue'* ]] || exit 1 ;;
    esac
done
print 'gwl checks passed'
ZSH
