#!/bin/bash
set -euo pipefail

if [ -n "${VPS:-}" ]; then
  echo "skip AI tooling installation on VPS host" >&2
  exit 0
fi

# claude-code 使用官方安装脚本
curl -fsSL https://claude.ai/install.sh | bash

NVM_DIR="${NVM_DIR:-$HOME/.nvm}"

# shellcheck disable=SC1090
if [ -s "$NVM_DIR/nvm.sh" ]; then
  . "$NVM_DIR/nvm.sh"
else
  echo "nvm not found; install it before running this script." >&2
  exit 1
fi

if nvm alias default >/dev/null 2>&1; then
  nvm use default >/dev/null
fi

if ! command -v npm >/dev/null 2>&1; then
  echo "npm not found; ensure Node.js is installed via nvm." >&2
  exit 1
fi

npm install -g @openai/codex opencommit

if ! command -v uv >/dev/null 2>&1; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl not found; install it before running uv installer." >&2
    exit 1
  fi
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi
