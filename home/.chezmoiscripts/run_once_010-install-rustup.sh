#!/bin/bash
set -euo pipefail

if [ -n "${VPS:-}" ]; then
  echo "skip rustup installation on VPS host" >&2
  exit 0
fi

# Check if rustup is already installed
if command -v rustup >/dev/null 2>&1; then
  echo "rustup already installed, skipping installation" >&2
  exit 0
fi

# Install rustup
echo "Installing rustup..." >&2
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y

# shellcheck disable=SC1090
if [ -f "$HOME/.cargo/env" ]; then
  . "$HOME/.cargo/env"
fi

