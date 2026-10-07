# 环境安装

脚本需由 root 或具备 sudo 权限的用户通过 Bash 执行。非 root 用户先运行 `sudo -v`。Linux 会安装软件、配置系统并应用 dotfiles；macOS 会应用配置和安装 Shell 插件，Homebrew 清单需单独执行。

Linux 上存在 `sshd` 时，应用 SSH 安全配置要求目标用户的 `~/.ssh/authorized_keys` 非空，否则会停止。已部署的机器应先确认公钥登录可用；新用户可通过下方的 `GITHUB_USER` 导入公钥。

## 安装

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

## 默认安装清单

Linux 默认安装以下工具：

- APT：zsh、bash-completion、hstr、coreutils、gawk、ripgrep、fd-find、fzf、tree、bat、unzip、bzip2、vim、neovim、git、git-lfs、tig、htop、dnsutils、net-tools、iperf3、ifstat、mtr-tiny、socat、telnet、curl、wget、httpie、jq、tmux、fail2ban。
- jd：gh、zoxide、yq（Mike Farah 版本）、zellij、croc、nexttrace、mihomo、uv。
- 官方发布包：tldr（tlrc 的 musl 二进制）、yt-dlp。当前 jd 发布版没有这两个工具的 Linux 二进制安装路径。
- uv：pre-commit、git-filter-repo，避免 APT 的 nodeenv 依赖拉入编译工具，并支持 Debian 11。
- Shell：oh-my-zsh、zsh-autosuggestions、fast-syntax-highlighting、zsh-wakatime、powerlevel10k，以及仓库中的 zsh 配置。默认主题保持 alanpeabody，可自行切换到 powerlevel10k。
- 服务与系统：Docker 官方一键脚本（get.docker.com）、非 root 用户加入 docker 组、Tailscale、ZeroTier、IPv4/IPv6 转发、禁用 SSH 密码和交互式认证，以及 Fail2ban 配置。SSH 配置在重载前校验；Tailscale、ZeroTier 安装后仍需自行登录或加入网络，WSL 会跳过这两个工具；mihomo 只安装命令，不写入代理配置或启动服务。

默认不安装 glab、splitrail、Rust、Node、Go 开发工具、AI CLI、Kubernetes CLI、QEMU 和媒体处理工具。Linux 不下发桌面和 AI 配置；Neovim 使用系统包和默认配置，避免开发环境的插件自动下载工具链。已有软件不自动卸载。

`jd` 和 `uv` 安装到 `~/.local/bin`，`batcat`、`fdfind` 分别映射为 `bat`、`fd`。Python 是 httpie、pre-commit、fail2ban 等工具的依赖，`python3-systemd` 用于 fail2ban 读取 SSH 日志。可以设置 `GITHUB_TOKEN`，避免多个安装共用出口 IP 时触发 GitHub API 限流。

## 从本地仓库安装

如果已经克隆了仓库到本地：

```bash
./install.sh
```

## 安装参数与 Linux 用户

脚本需由 root 或具备 sudo 权限的用户执行。在 Linux 上可通过环境变量创建带 sudo 的用户，并将指定 GitHub 用户的公钥写入其 `~/.ssh/authorized_keys`（仅 Linux，macOS 不创建用户）：

| 变量 | 说明 |
|------|------|
| `CHEZMOI_SOURCE` | 使用指定的本地源目录，优先于 `CHEZMOI_REPO` |
| `CHEZMOI_REPO` | 使用指定 GitHub 用户名或仓库 URL；未设置时优先使用检测到的本地仓库，否则使用 `jimyag` |
| `CREATE_USER` | Linux 上创建或复用指定用户，并以该用户应用配置；新建用户获免密码 sudo 权限，不设置时使用当前用户 |
| `GITHUB_USER` | 配合 `CREATE_USER`，将该 GitHub 用户的公钥合并到目标用户的 `authorized_keys`；不设置则不拉取 |
| `SET_HOSTNAME` | Linux 上有 `hostnamectl` 时设置主机名；不设置则保留原值 |
| `GITHUB_TOKEN` | 为 CLI 安装脚本和 GitHub API 请求提供认证，减少共享出口的限流 |

创建用户 `jimyag` 并写入其 GitHub 公钥：

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=jimyag GITHUB_USER=jimyag bash
```

创建自定义用户并导入公钥（示例：`myuser`）：

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=myuser GITHUB_USER=myuser bash
```

从本地仓库安装并设置主机名：

```bash
CREATE_USER=myuser GITHUB_USER=myuser SET_HOSTNAME=myserver ./install.sh
```

只创建用户时省略 `GITHUB_USER`；目标用户仍需自行准备公钥，才能通过 SSH 安全配置检查。远程管道安装的参数放在 `bash` 前，本地安装的参数放在 `./install.sh` 前。

## 手动安装

```bash
chezmoi init jimyag
chezmoi diff
chezmoi apply -v
```

手动应用也会执行适用的 Chezmoi 脚本。macOS 如需安装 Brewfile 中的软件，先检查清单，再执行：

```bash
brew bundle --file="$(chezmoi source-path)/Brewfile"
```

## 复用说明

如果想基于这个仓库维护自己的 dotfiles，可以先用 chezmoi 初始化到本地，再将远端改为自己的仓库：

```bash
chezmoi init jimyag
cd "$(chezmoi source-path)"
git remote set-url origin git@github.com:<your-user>/<your-dotfiles-repo>.git
```

之后至少检查并替换这些个人化内容：

- `home/dot_gitconfig` 中的 Git 用户名和邮箱
- README 和安装命令里的 `jimyag/dotfiles`
- `install.sh` 中未设置 `CHEZMOI_REPO` 时的默认 `chezmoi init --apply jimyag`
- `docs/private-public-repo-management.md` 和脚本提示里的示例仓库地址

也可以不修改脚本默认值，安装时显式指定自己的仓库：

```bash
CHEZMOI_REPO=<your-user>/<your-dotfiles-repo> ./install.sh
```

## Debian 11 归档源

Debian 11 的 LTS 已于 2026-08-31 结束，默认安全源可能仍提供索引但已移除包，导致 404。
安装前需要准备可用的归档源；安装器不自动覆盖已有的 APT 源。
需要复用 Debian 11 时，可参考以下归档源：

```text
deb [check-valid-until=no] http://archive.debian.org/debian bullseye main
deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20260831T235959Z bullseye-security main
```

快照保留 Debian 签名校验，但不提供后续安全更新。参见 [Debian 官方仓库迁移讨论](https://lists.debian.org/debian-mirrors/2026/09/msg00001.html)。
