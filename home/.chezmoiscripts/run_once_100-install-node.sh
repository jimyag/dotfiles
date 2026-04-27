#!/bin/bash
set -euo pipefail

export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

if [ -n "${VPS:-}" ]; then
  echo "skip nvm/node installation on VPS host" >&2
  exit 0
fi

NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
export NVM_DIR

sanitize_npmrc_for_nvm() {
  local npmrc backup
  npmrc="${HOME:?}/.npmrc"
  backup="${npmrc}.pre-nvm-backup"

  [ -f "$npmrc" ] || return 0

  if ! grep -Eq '^[[:space:]]*(prefix|globalconfig)[[:space:]]*=' "$npmrc"; then
    return 0
  fi

  cp "$npmrc" "$backup"
  grep -Ev '^[[:space:]]*(prefix|globalconfig)[[:space:]]*=' "$backup" >"$npmrc"
  echo "removed incompatible prefix/globalconfig from $npmrc for nvm; backup at $backup" >&2
}

if [ "${CHEZMOI_TEST_MODE:-}" = "1" ]; then
  return 0
fi

if [ ! -d "$NVM_DIR/.git" ]; then
  if [ -e "$NVM_DIR" ]; then
    echo "nvm directory exists but is not a git repo: $NVM_DIR" >&2
    exit 1
  fi
  git clone https://github.com/nvm-sh/nvm.git "$NVM_DIR"
fi

(
  cd "$NVM_DIR"
  git fetch --tags origin
  latest_ref="$(git rev-list --tags --max-count=1)"
  if [ -n "$latest_ref" ]; then
    latest_tag="$(git describe --tags "$latest_ref")"
    git checkout "$latest_tag"
  fi
)

# shellcheck source=/dev/null
if [ -s "$NVM_DIR/nvm.sh" ]; then
  . "$NVM_DIR/nvm.sh"
else
  echo "nvm.sh not found in $NVM_DIR" >&2
  exit 1
fi

sanitize_npmrc_for_nvm
nvm install node
nvm alias default node
