#!/bin/sh

set -e # -e: exit on error

if [ ! "$(command -v chezmoi)" ]; then
  bin_dir="$HOME/.local/bin"
  chezmoi="$bin_dir/chezmoi"
  if [ "$(command -v curl)" ]; then
    sh -c "$(curl -fsSL https://git.io/chezmoi)" -- -b "$bin_dir"
  elif [ "$(command -v wget)" ]; then
    sh -c "$(wget -qO- https://git.io/chezmoi)" -- -b "$bin_dir"
  else
    echo "To install chezmoi, you must have curl or wget installed." >&2
    exit 1
  fi
else
  chezmoi=chezmoi
fi

# POSIX way to get script's dir: https://stackoverflow.com/a/29834779/12156188
script_dir="$(cd -P -- "$(dirname -- "$(command -v -- "$0")")" && pwd -P)"

# Support environment variables for configuration
# CHEZMOI_SOURCE: local source directory (overrides script_dir)
# CHEZMOI_REPO: GitHub username or repo URL (e.g., "jimyag" or "github.com/jimyag/dotfiles")
# VPS: set to non-empty value to skip certain installations on VPS hosts
# If both CHEZMOI_SOURCE and CHEZMOI_REPO are set, CHEZMOI_SOURCE takes precedence

# Export VPS variable so it's available to chezmoi scripts
export VPS="${VPS:-}"

# Disable git config to use HTTPS instead of SSH for chezmoi operations
# This prevents "Permission denied (publickey)" errors when updating chezmoi
# on systems without SSH keys configured
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

if [ -n "${CHEZMOI_SOURCE:-}" ]; then
  # Use specified source directory
  exec "$chezmoi" init --apply "--source=$CHEZMOI_SOURCE"
elif [ -n "${CHEZMOI_REPO:-}" ]; then
  # Use specified GitHub repo or username
  exec "$chezmoi" init --apply "$CHEZMOI_REPO"
elif [ -d "$script_dir/home" ] || [ -d "$script_dir/.chezmoiscripts" ]; then
  # Auto-detect: if script is in a chezmoi source directory, use it
  exec "$chezmoi" init --apply "--source=$script_dir"
else
  # Default: use GitHub username
  exec "$chezmoi" init --apply jimyag
fi