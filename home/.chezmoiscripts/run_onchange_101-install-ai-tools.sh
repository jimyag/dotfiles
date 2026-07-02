#!/bin/bash
set -euo pipefail

if [ "${VPS:-}" = "1" ]; then
  echo "skip AI tooling installation on VPS host" >&2
  exit 0
fi

# claude-code 使用官方安装脚本
if command -v claude >/dev/null 2>&1; then
  echo "skip Claude Code install: command already exists" >&2
else
  curl -fsSL https://claude.ai/install.sh | bash
fi

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

ensure_npm_global_package() {
  local package="$1"
  if npm ls -g "$package" --depth=0 >/dev/null 2>&1; then
    echo "skip npm global install: $package already installed" >&2
    return 0
  fi
  npm install -g "$package"
}

for package in \
  @openai/codex \
  @pencil.dev/cli@0.2.7 \
  opencommit \
  @github/copilot \
  @google/gemini-cli \
  @wecom/cli \
  deepseek-tui \
  happy-coder \
  mcporter
do
  ensure_npm_global_package "$package"
done

if ! command -v uv >/dev/null 2>&1; then
  if ! command -v curl >/dev/null 2>&1; then
    echo "curl not found; install it before running uv installer." >&2
    exit 1
  fi
  curl -LsSf https://astral.sh/uv/install.sh | sh
else
  echo "skip uv install: command already exists" >&2
fi
