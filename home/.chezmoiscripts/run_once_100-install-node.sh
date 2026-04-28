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

nvm install node
nvm alias default node
