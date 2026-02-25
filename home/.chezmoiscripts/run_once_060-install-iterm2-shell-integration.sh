#!/bin/bash
set -euo pipefail

INSTALL_URL="https://iterm2.com/shell_integration/install_shell_integration_and_utilities.sh"

if [ "$(uname -s)" = "Darwin" ]; then
  echo "skip iTerm2 shell integration installer on macOS" >&2
  exit 0
fi

if ! command -v curl >/dev/null 2>&1; then
  echo "curl not found; skip iTerm2 shell integration installation" >&2
  exit 0
fi

if ! command -v bash >/dev/null 2>&1; then
  echo "bash not found; skip iTerm2 shell integration installation" >&2
  exit 0
fi

install_for_shell() {
  local shell_name="$1"
  local target_file="$HOME/.iterm2_shell_integration.${shell_name}"

  if ! command -v "$shell_name" >/dev/null 2>&1; then
    return
  fi

  if [ -s "$target_file" ]; then
    echo "iTerm2 shell integration already exists for ${shell_name}, skipping" >&2
    return
  fi

  echo "install iTerm2 shell integration for ${shell_name}" >&2
  curl -fsSL "$INSTALL_URL" | SHELL="$shell_name" bash
}

for shell_name in zsh bash fish tcsh; do
  install_for_shell "$shell_name"
done
