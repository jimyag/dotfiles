#!/bin/bash
# Run in a disposable Debian/Ubuntu container.
set -euo pipefail
repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Debian 11 is EOL; pin its retired repositories only in this disposable fixture.
. /etc/os-release
if [ "$ID" = debian ] && [ "$VERSION_ID" = 11 ]; then
    printf '%s\n' \
        'deb [check-valid-until=no] http://archive.debian.org/debian bullseye main' \
        'deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20260831T235959Z bullseye-security main' \
        > /etc/apt/sources.list
fi

apt-get update
DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends ca-certificates curl openssh-server
mkdir -p /run/sshd "$HOME/.ssh"
if [ ! -f /tmp/dotfiles-test-key ]; then
    ssh-keygen -q -t ed25519 -N '' -f /tmp/dotfiles-test-key
fi
install -m 0600 /tmp/dotfiles-test-key.pub "$HOME/.ssh/authorized_keys"

CHEZMOI_SOURCE="$repo_root" bash "$repo_root/install.sh"
export PATH="$HOME/.local/bin:$PATH"

for tool in zsh hstr rg fd fzf zoxide tree bat unzip bzip2 tldr vim nvim \
    git gh git-lfs git-filter-repo tig pre-commit htop dig ifconfig \
    iperf3 ifstat mtr socat telnet curl wget http jq yq zellij docker \
    tailscale zerotier-cli uv croc tmux fail2ban-client nexttrace jd mihomo yt-dlp; do
    command -v "$tool"
done

for tool in glab splitrail rustup cargo rustc node npm claude codex kubectl kubebuilder qemu-system-x86_64; do
    if command -v "$tool" >/dev/null 2>&1; then
        echo "Unexpected default tool: $tool" >&2
        exit 1
    fi
done

for plugin in zsh-autosuggestions fast-syntax-highlighting zsh-wakatime; do
    test -d "$HOME/.oh-my-zsh/custom/plugins/$plugin"
done
test -d "$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
test ! -d "$HOME/.config/nvim"
test ! -d "$HOME/.agents"
sshd -t
sshd_config="$(sshd -T)"
grep -qx 'passwordauthentication no' <<< "$sshd_config"
grep -qx 'kbdinteractiveauthentication no' <<< "$sshd_config"
grep -qx 'net.ipv4.ip_forward = 1' /etc/sysctl.d/99-dotfiles-forwarding.conf
grep -qx 'net.ipv6.conf.all.forwarding = 1' /etc/sysctl.d/99-dotfiles-forwarding.conf

yq --version
tldr --version
zoxide --version
zellij --version
croc --version
nexttrace --version
mihomo -v
yt-dlp --version
uv --version
pre-commit --version
git init -q /tmp/dotfiles-test-repo
git -C /tmp/dotfiles-test-repo status --porcelain
nvim --clean --headless '+quit'
zsh -ic 'command -v rg fd bat zoxide jd; test "$ZSH_THEME" = alanpeabody'
cmp "$repo_root/home/dot_zshrc" "$HOME/.zshrc"
fail2ban-client -t

CHEZMOI_SOURCE="$repo_root" bash "$repo_root/install.sh"
cmp "$repo_root/home/dot_zshrc" "$HOME/.zshrc"
echo "PASS: $(. /etc/os-release; echo "$PRETTY_NAME")"
