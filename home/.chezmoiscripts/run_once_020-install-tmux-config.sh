#!/bin/bash
set -euo pipefail

# Check if tmux is installed
if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found; please install tmux first" >&2
  exit 1
fi

# Install .tmux configuration (will overwrite existing configuration)
echo "Installing .tmux configuration..." >&2
tmp_install_script="$(mktemp)"
trap 'rm -f "$tmp_install_script"' EXIT
curl -fsSL "https://raw.githubusercontent.com/gpakosz/.tmux/master/install.sh?ts=$(date +%s)" -o "$tmp_install_script"
bash "$tmp_install_script" </dev/null
