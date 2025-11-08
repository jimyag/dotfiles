#!/bin/bash
set -euo pipefail

if [ -n "${VPS:-}" ]; then
  echo "skip cargo binary installation on VPS host" >&2
  exit 0
fi


# shellcheck disable=SC1090
if [ -f "$HOME/.cargo/env" ]; then
  . "$HOME/.cargo/env"
fi

if ! command -v cargo >/dev/null 2>&1; then
  echo "cargo not found; run rustup install first" >&2
  exit 1
fi

cargo install tlrc --locked
