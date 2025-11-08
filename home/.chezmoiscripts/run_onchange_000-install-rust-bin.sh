#!/bin/bash
set -euo pipefail

if [ -n "${VPS:-}" ]; then
  echo "skip cargo binary installation on VPS host" >&2
  exit 0
fi

curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# shellcheck disable=SC1091
if [ -s "$HOME/.cargo/env" ]; then
  . "$HOME/.cargo/env"
fi

cargo install tlrc --locked