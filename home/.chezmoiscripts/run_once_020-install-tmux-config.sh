#!/bin/bash
set -euo pipefail

# Check if tmux is installed
if ! command -v tmux >/dev/null 2>&1; then
  echo "tmux not found; please install tmux first" >&2
  exit 1
fi

# Install .tmux configuration (will overwrite existing configuration)
echo "Installing .tmux configuration..." >&2
curl -fsSL "https://github.com/gpakosz/.tmux/raw/refs/heads/master/install.sh#$(date +%s)" | bash

