# dotfiles

这是我的个人 dotfiles 仓库，里面有一些写死的个人配置，例如默认仓库 `jimyag/dotfiles`、默认 `chezmoi init jimyag`、Git 用户信息、邮箱和部分脚本提示。直接使用前建议先通读并替换为自己的值。

[![Check](https://github.com/jimyag/dotfiles/actions/workflows/check.yaml/badge.svg)](https://github.com/jimyag/dotfiles/actions/workflows/check.yaml)

## Agent Skills

根目录的 `skills/` 包含可复用的 Agent Skills，可以直接通过 `npx skills`
查看或安装：

```bash
# 查看仓库中可用的 skills
npx skills add jimyag/dotfiles --list

# 安装全部 skills
npx skills add jimyag/dotfiles --all

# 安装指定 skill
npx skills add jimyag/dotfiles --skill systematic-debugging
```

`home/dot_agents/skills` 是指向根目录 `skills/` 的相对软链接，用于通过
Chezmoi 将同一份内容应用到 `~/.agents/skills/`，避免维护两份副本。

部分 skill 使用 Claude Code/Codex 的扩展 frontmatter，或依赖同级
`_shared/` 规则；这些兼容性要求会在各自的 `SKILL.md` 中说明。第三方来源
及许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

## 复用说明

如果想基于这个仓库维护自己的 dotfiles，可以先用 chezmoi 初始化到本地，再断开原仓库并换成自己的仓库：

```bash
chezmoi init jimyag
cd "$(chezmoi source-path)"
rm -rf .git
git init
git remote add origin git@github.com:<your-user>/<your-dotfiles-repo>.git
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

## 一键安装

安装脚本需 **bash** 执行（管道安装请使用 `| bash`）。

### 安装

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

### 默认安装清单

Linux 使用下面这一份清单，没有 VPS/开发模式切换：

- APT：zsh、bash-completion、hstr、coreutils、gawk、ripgrep、fd-find、fzf、tree、bat、unzip、bzip2、vim、neovim、git、git-lfs、tig、htop、dnsutils、net-tools、iperf3、ifstat、mtr-tiny、socat、telnet、curl、wget、httpie、jq、tmux、fail2ban。
- jd：gh、zoxide、yq（Mike Farah 版本）、zellij、croc、nexttrace、mihomo、uv。
- 官方发布包：tldr（tlrc 的 musl 二进制）、yt-dlp。当前 jd 发布版没有这两个工具的 Linux 二进制安装路径。
- uv：pre-commit、git-filter-repo，避免 APT 的 nodeenv 依赖拉入编译工具，并支持 Debian 11。
- Shell：oh-my-zsh、zsh-autosuggestions、fast-syntax-highlighting、zsh-wakatime、powerlevel10k，以及仓库中的 zsh 配置。默认主题保持 alanpeabody，可自行切换到 powerlevel10k。
- 服务与系统：Docker 官方一键脚本（get.docker.com）、非 root 用户加入 docker 组、Tailscale、ZeroTier、IPv4/IPv6 转发、禁用 SSH 密码和交互式认证。SSH 修改要求当前用户已有 `authorized_keys`，并在重载前校验配置。Tailscale、ZeroTier 安装后仍需自行登录或加入网络；mihomo 只安装命令，不写入代理配置或启动服务。

默认不安装 glab、splitrail、Rust、Node、Go 开发工具、AI CLI、Kubernetes CLI、QEMU 和媒体处理工具。Linux 不下发桌面和 AI 配置；Neovim 使用系统包和默认配置，避免开发环境的插件自动下载工具链。已有软件不自动卸载。

`jd` 和 `uv` 安装到 `~/.local/bin`，`batcat`、`fdfind` 分别映射为 `bat`、`fd`。Python 是 httpie、pre-commit、fail2ban 等工具的依赖，`python3-systemd` 用于 fail2ban 读取 SSH 日志。可以设置 `GITHUB_TOKEN`，避免多个安装共用出口 IP 时触发 GitHub API 限流。

### 从本地仓库安装

如果已经克隆了仓库到本地：

```bash
./install.sh
```

### Linux 上创建用户并配置 SSH

脚本需由 root 或具备 sudo 权限的用户执行。在 Linux 上可通过环境变量创建带 sudo 的用户，并将指定 GitHub 用户的公钥写入其 `~/.ssh/authorized_keys`（仅 Linux，macOS 不创建用户）：

| 变量 | 说明 |
|------|------|
| `CREATE_USER` | 要创建的用户名；不设置时不创建用户，设为非空时在 Linux 上执行创建用户和/或更新 SSH 授权 |
| `GITHUB_USER` | 指定时将该 GitHub 用户的公钥写入对应用户的 `~/.ssh/authorized_keys`，不设则不拉取 |

**仅要求 sudo，不创建用户（默认行为）：**

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

**创建用户 jimyag 并写入其 GitHub 公钥：**

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=jimyag GITHUB_USER=jimyag bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=jimyag GITHUB_USER=jimyag bash
```

**创建自定义用户并写入其 GitHub 公钥（示例：myuser）：**

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=myuser GITHUB_USER=myuser bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=myuser GITHUB_USER=myuser bash
```

**只创建用户 jimyag，不拉取 GitHub 公钥：**

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=jimyag bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | CREATE_USER=jimyag bash
```

**从本地仓库安装时：**

```bash
# 仅要求 sudo，不创建用户
./install.sh

# 创建用户 jimyag 并写入 GitHub 公钥
CREATE_USER=jimyag GITHUB_USER=jimyag ./install.sh

# 创建自定义用户 myuser 并写入 GitHub 公钥
CREATE_USER=myuser GITHUB_USER=myuser ./install.sh

# 只创建用户 jimyag
CREATE_USER=jimyag ./install.sh
```

## 手动安装

```bash
chezmoi init jimyag

chezmoi apply -v
```

## 常用命令

```bash
chezmoi add ~/.zshrc --template

chezmoi diff

chezmoi apply -v
```

## 开发

`gwl` 列出当前仓库的 worktree，并查询本人最近 100 个 PR（含已关闭、已合并）。
优先匹配 `upstream`，再匹配 `origin`；没有 `upstream` 时，自动查询 fork 的上游仓库。
PR 的关联 Issue 会显示在 ISSUE 列；没有关联信息时，尝试从 `issue-<数字>` 分支查询。
找不到匹配 PR 或 GitHub 查询失败时，会在标准错误中提示。

修改 `gwl` 后可运行 `bash scripts/test-gwl.sh` 验证查询与回退行为。

提交和 PR 会检查安装脚本与辅助脚本的 Bash 语法。可在本地运行：

```bash
bash -n install.sh scripts/sync_public_dotfiles.sh skills/codecov-coverage/scripts/*.sh
```

在干净容器中验证默认安装、工具运行、SSH 配置、zsh 启动及重复安装：

```bash
docker run --rm -v "$PWD:/src:ro" debian:13-slim bash -c 'cp -a /src /tmp/dotfiles; bash /tmp/dotfiles/scripts/test-linux-install.sh'
```

同样检查 `debian:11-slim`、`debian:12-slim`、`ubuntu:22.04`、`ubuntu:24.04`、`ubuntu:26.04`。
容器内只验证服务软件安装和持久配置；服务启动、实时转发和 SSH 登录需要在真实主机上验证。

Debian 11 的 LTS 已于 2026-08-31 结束，默认安全源可能仍提供索引但已移除包，导致 404。
安装前需要准备可用的归档源；安装器不自动覆盖已有的 APT 源。
本次兼容性验证使用官方 Debian 归档和最后一天的安全仓库快照：

```text
deb [check-valid-until=no] http://archive.debian.org/debian bullseye main
deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20260831T235959Z bullseye-security main
```

快照保留 Debian 签名校验，但不提供后续安全更新。参见 [Debian 官方仓库迁移讨论](https://lists.debian.org/debian-mirrors/2026/09/msg00001.html)。

## 进阶用法

- [使用私有和公开仓库管理配置](docs/private-public-repo-management.md)

## 其他

```bash
brew bundle dump --file=~/.local/share/chezmoi/home/Brewfile
```
