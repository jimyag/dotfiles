#!/bin/bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
export STARSHIP_CONFIG="$repo_root/home/dot_config/starship.toml"
export TERM=xterm-256color
tmpdir="$(mktemp -d)"
trap 'rm -rf "$tmpdir"' EXIT
export STARSHIP_CACHE="$tmpdir/cache"

command -v starship >/dev/null
prompt="$(starship prompt --path "$tmpdir" --logical-path "$tmpdir" --status 0 2>"$tmpdir/stderr")"
test ! -s "$tmpdir/stderr"
[[ "$prompt" == *"$(id -un)"* && "$prompt" == *'@'* && "$prompt" == *"$tmpdir"* && "$prompt" == *'$ '* ]]
[[ "$prompt" != *$'\n'* && "$prompt" != *''* && "$prompt" != *'('* ]]

prompt="$(starship prompt --right --path "$tmpdir" --logical-path "$tmpdir" --status 42 --cmd-duration 5000 2>"$tmpdir/stderr")"
test ! -s "$tmpdir/stderr"
[[ "$prompt" == *'42 ↵'* && "$prompt" == *'5s'* ]]

git init -q "$tmpdir/repo"
git -C "$tmpdir/repo" checkout -qb prompt-check
git -C "$tmpdir/repo" -c user.name=Test -c user.email=test@example.invalid \
    -c commit.gpgsign=false -c core.hooksPath=/dev/null commit --allow-empty -qm fixture
prompt="$(starship prompt --path "$tmpdir/repo" --logical-path "$tmpdir/repo" --status 0 2>"$tmpdir/stderr")"
test ! -s "$tmpdir/stderr"
[[ "$prompt" == *'('* && "$prompt" == *'prompt-check'* && "$prompt" == *') $ '* ]]
touch "$tmpdir/repo/untracked"
prompt="$(starship prompt --path "$tmpdir/repo" --logical-path "$tmpdir/repo" --status 0 2>"$tmpdir/stderr")"
test ! -s "$tmpdir/stderr"
[[ "$prompt" == *'?'* ]]

zsh -f -ic '
    source "$1" &&
    (( $+functions[prompt_starship_precmd] )) &&
    [[ "${precmd_functions[(Ie)prompt_starship_precmd]}" -gt 0 ]]
' -- "$repo_root/home/dot_profile.d/zsh-prompt"

echo 'Starship checks passed'
