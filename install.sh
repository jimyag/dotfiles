#!/bin/sh

set -e # -e: exit on error

# 必须由具备 sudo 权限的用户执行
if ! sudo -n true 2>/dev/null; then
  echo "此脚本需要由具备 sudo 权限的用户执行，请先执行 sudo -v 或使用 sudo 运行。" >&2
  exit 1
fi

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
# CREATE_USER: 在 Linux 上创建带 sudo 的用户，值为用户名，默认为 jimyag（仅 Linux，macOS 不创建用户）
# GITHUB_USER: 指定时将该 GitHub 用户的公钥写入对应用户的 ~/.ssh/authorized_keys，默认不拉取
# If both CHEZMOI_SOURCE and CHEZMOI_REPO are set, CHEZMOI_SOURCE takes precedence

# Export VPS variable so it's available to chezmoi scripts
export VPS="${VPS:-}"

# 仅 Linux 且 CREATE_USER 非空时：创建用户（useradd）或用户已存在时仅更新 SSH 授权
add_user="${CREATE_USER:-jimyag}"
# 用户名禁止含 /、..、空格，避免路径穿越与 useradd 异常
case "$add_user" in
  */*|*..*|*' '*|'')
    [ -n "${CREATE_USER:-}" ] && [ "$(uname)" = "Linux" ] && echo "CREATE_USER 含非法字符或为空，跳过创建用户。" >&2
    ;;
  *)
if [ -n "${CREATE_USER:-}" ] && [ "$(uname)" = "Linux" ]; then
  if ! id "$add_user" >/dev/null 2>&1; then
    sudo useradd -m -s /bin/bash "$add_user"
    echo "$add_user ALL=(ALL) NOPASSWD: ALL" | sudo tee "/etc/sudoers.d/$add_user" >/dev/null
  fi
  if [ -n "${GITHUB_USER:-}" ]; then
    keys_url="https://github.com/${GITHUB_USER}.keys"
    user_home=$(getent passwd "$add_user" 2>/dev/null | cut -d: -f6) || user_home="/home/$add_user"
    ssh_dir="$user_home/.ssh"
    auth_keys="$ssh_dir/authorized_keys"
    if [ -d "$user_home" ]; then
      sudo mkdir -p "$ssh_dir"
      sudo chmod 700 "$ssh_dir"
      if [ "$(command -v curl)" ]; then
        if curl -fsSL "$keys_url" | sudo tee "$auth_keys" >/dev/null; then
          sudo chmod 600 "$auth_keys"
          sudo chown -R "$add_user:$add_user" "$ssh_dir"
        else
          echo "拉取 GitHub 公钥失败，跳过 GITHUB_USER。" >&2
        fi
      elif [ "$(command -v wget)" ]; then
        if wget -qO- "$keys_url" | sudo tee "$auth_keys" >/dev/null; then
          sudo chmod 600 "$auth_keys"
          sudo chown -R "$add_user:$add_user" "$ssh_dir"
        else
          echo "拉取 GitHub 公钥失败，跳过 GITHUB_USER。" >&2
        fi
      else
        echo "需要 curl 或 wget 以拉取 GitHub 公钥，跳过 GITHUB_USER。" >&2
      fi
    fi
  fi
fi
;;
esac

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