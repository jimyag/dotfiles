#!/bin/bash
# 需 bash（若用 curl 安装请：curl ... | bash）
set -e

# 必须由具备 sudo 权限的用户执行
if ! sudo -n true 2>/dev/null; then
  echo "此脚本需要由具备 sudo 权限的用户执行，请先执行 sudo -v 或使用 sudo 运行。" >&2
  exit 1
fi

# 环境变量说明见下方，先统一导出
export VPS="${VPS:-}"
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

# CHEZMOI_SOURCE: 本地 dotfiles 目录
# CHEZMOI_REPO: GitHub 用户名或仓库 URL
# CREATE_USER: Linux 上要创建的用户名（如 jimyag），非空则先创建用户再切到该用户执行 chezmoi
# GITHUB_USER: 将该 GitHub 用户的公钥写入对应用户 ~/.ssh/authorized_keys

add_user="${CREATE_USER:-jimyag}"

# 安装 chezmoi 到当前用户的 ~/.local/bin（若尚未安装）
ensure_chezmoi() {
  if command -v chezmoi >/dev/null 2>&1; then return; fi
  local bin_dir="${HOME:?}/.local/bin"
  mkdir -p "$bin_dir"
  if command -v curl >/dev/null 2>&1; then
    sh -c "$(curl -fsSL https://git.io/chezmoi)" -- -b "$bin_dir"
  elif command -v wget >/dev/null 2>&1; then
    sh -c "$(wget -qO- https://git.io/chezmoi)" -- -b "$bin_dir"
  else
    echo "To install chezmoi, you need curl or wget." >&2
    exit 1
  fi
}

# 执行 chezmoi init --apply（依赖 CHEZMOI_SOURCE / CHEZMOI_REPO / SCRIPT_DIR）
run_chezmoi_apply() {
  export PATH="${HOME:?}/.local/bin:$PATH"
  ensure_chezmoi
  if [ -n "${CHEZMOI_SOURCE:-}" ]; then
    exec chezmoi init --apply "--source=$CHEZMOI_SOURCE"
  fi
  if [ -n "${CHEZMOI_REPO:-}" ]; then
    exec chezmoi init --apply "$CHEZMOI_REPO"
  fi
  if [ -n "${SCRIPT_DIR:-}" ] && { [ -d "$SCRIPT_DIR/home" ] || [ -d "$SCRIPT_DIR/.chezmoiscripts" ]; }; then
    exec chezmoi init --apply "--source=$SCRIPT_DIR"
  fi
  exec chezmoi init --apply jimyag
}

# 创建用户并配置 SSH 公钥（仅 Linux，CREATE_USER 非空时）
create_user_and_ssh() {
  local u="$1"
  local keys_url user_home ssh_dir auth_keys

  if ! id "$u" >/dev/null 2>&1; then
    sudo useradd -m -s /bin/bash "$u"
    echo "$u ALL=(ALL) NOPASSWD: ALL" | sudo tee "/etc/sudoers.d/$u" >/dev/null
  fi

  if [ -z "${GITHUB_USER:-}" ]; then return; fi
  keys_url="https://github.com/${GITHUB_USER}.keys"
  user_home=$(getent passwd "$u" 2>/dev/null | cut -d: -f6) || user_home="/home/$u"
  ssh_dir="$user_home/.ssh"
  auth_keys="$ssh_dir/authorized_keys"
  [ ! -d "$user_home" ] && return

  sudo mkdir -p "$ssh_dir"
  sudo chmod 700 "$ssh_dir"
  if command -v curl >/dev/null 2>&1; then
    curl -fsSL "$keys_url" | sudo tee "$auth_keys" >/dev/null || { echo "拉取 GitHub 公钥失败。" >&2; return; }
  elif command -v wget >/dev/null 2>&1; then
    wget -qO- "$keys_url" | sudo tee "$auth_keys" >/dev/null || { echo "拉取 GitHub 公钥失败。" >&2; return; }
  else
    echo "需要 curl 或 wget 以拉取 GitHub 公钥。" >&2
    return
  fi
  sudo chmod 600 "$auth_keys"
  sudo chown -R "$u:$u" "$ssh_dir"
}

# 用户名合法：不含 /、..、空格
is_valid_username() {
  case "$1" in
    */*|*..*|*' '*|'') return 1 ;;
    *) return 0 ;;
  esac
}

# 当前脚本目录（用于本地仓库自动探测）
SCRIPT_DIR="$(cd -P -- "$(dirname -- "${BASH_SOURCE[0]:-$0}")" && pwd -P)"

# --- 主流程 ---
if [ -n "${CREATE_USER:-}" ] && [ "$(uname)" = "Linux" ] && is_valid_username "$add_user"; then
  create_user_and_ssh "$add_user"
  target_home=$(getent passwd "$add_user" 2>/dev/null | cut -d: -f6) || target_home="/home/$add_user"
  exec sudo -u "$add_user" env \
    HOME="$target_home" USER="$add_user" LOGNAME="$add_user" \
    VPS="$VPS" CHEZMOI_SOURCE="${CHEZMOI_SOURCE:-}" CHEZMOI_REPO="${CHEZMOI_REPO:-}" SCRIPT_DIR="$SCRIPT_DIR" \
    GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 \
    bash -c 'source /dev/stdin' << DECLARE_AND_RUN
$(declare -f ensure_chezmoi run_chezmoi_apply)
run_chezmoi_apply
DECLARE_AND_RUN
fi

if [ -n "${CREATE_USER:-}" ] && [ "$(uname)" = "Linux" ] && ! is_valid_username "$add_user"; then
  echo "CREATE_USER 含非法字符或为空，跳过创建用户。" >&2
fi

# 不创建用户：在当前用户下执行
run_chezmoi_apply
