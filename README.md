# dotfiles

我的个人 dotfiles、环境初始化脚本和 Agent Skills，由 Chezmoi 管理。可以单独安装技能，也可以使用整套配置初始化 macOS 或 Linux 环境。

[![Check](https://github.com/jimyag/dotfiles/actions/workflows/check.yaml/badge.svg)](https://github.com/jimyag/dotfiles/actions/workflows/check.yaml)

[仓库功能](#仓库功能) · [Agent Skills](#agent-skills) · [复用说明](#复用说明) · [环境安装](#环境安装) · [开发与验证](#开发与验证)

## 仓库功能

- Shell 与 Git：zsh、oh-my-zsh 插件、别名、函数和 Git 配置；`gwl` 可查看 worktree 及关联的 GitHub PR。
- macOS 配置：Homebrew 软件清单、Neovim、Ghostty、Kitty、Zellij 和 Hammerspoon 配置。Brewfile 单独维护，安装脚本不会自动执行 `brew bundle`。
- Linux 初始化：安装常用命令行工具、Docker 和网络工具，配置 SSH 公钥认证、Fail2ban 与 IP 转发；可创建用户、导入 GitHub 公钥和设置主机名。
- Agent Skills：需求澄清、调试、评审、GitHub 交付、技术写作、技能维护和专项分析，可通过 `npx skills` 独立安装。

整套配置包含个人 Git 身份、默认仓库和应用偏好。复用前请检查下方的[复用说明](#复用说明)。Linux 初始化会修改系统配置；执行前需确认目标机器和 SSH 公钥已准备好。

### 目录

| 路径 | 内容 |
| --- | --- |
| [skills/](skills/) | 可独立安装的技能及其参考资料、脚本和评测场景 |
| [home/](home/) | Chezmoi 管理的配置，`dot_` 映射为点文件，`.tmpl` 表示模板 |
| [home/.chezmoiscripts/](home/.chezmoiscripts/) | 随 Chezmoi 应用执行的安装与系统配置脚本 |
| [home/Brewfile](home/Brewfile) | macOS 的 Homebrew、应用和开发工具清单 |
| [install.sh](install.sh) | 环境初始化入口 |
| [scripts/](scripts/) | 公开与私有配置同步、安装验证等辅助脚本 |
| [docs/](docs/) | 公开与私有仓库管理说明 |

## Agent Skills

技能按任务使用，点击名称可查看触发条件、流程和依赖。各技能的读写与授权规则见对应 `SKILL.md`；其中 `ai-review-loop` 必须明确点名才会启用。

### 开发与交付

| 技能 | 用途 |
| --- | --- |
| [brainstorming](skills/brainstorming/SKILL.md) | 澄清目标、范围和关键假设，收敛实现方案 |
| [writing-plans](skills/writing-plans/SKILL.md) | 为有多阶段依赖的实现编写执行计划 |
| [systematic-debugging](skills/systematic-debugging/SKILL.md) | 用证据和最小复现定位缺陷、测试或构建失败 |
| [test-scenarios](skills/test-scenarios/SKILL.md) | 整理测试计划、验收标准与 E2E 场景 |
| [requesting-code-review](skills/requesting-code-review/SKILL.md) | 只读审查代码差异或 PR，检查正确性和复杂度 |
| [receiving-code-review](skills/receiving-code-review/SKILL.md) | 核实评审反馈，再处理成立的问题 |
| [simplify](skills/simplify/SKILL.md) | 保持行为不变，简化近期改动 |
| [fix-merge-conflicts](skills/fix-merge-conflicts/SKILL.md) | 解决 merge、rebase 或 cherry-pick 冲突并验证 |
| [git-commit](skills/git-commit/SKILL.md) | 精准暂存并生成规范提交，按授权推送 |
| [pull-request](skills/pull-request/SKILL.md) | 创建 PR，或整理标题、正文与模板 |
| [gh-stack](skills/gh-stack/SKILL.md) | 管理相互依赖的分支和堆叠 PR |
| [loop-on-ci](skills/loop-on-ci/SKILL.md) | 跟踪 Actions、修复失败并验证检查结果 |
| [ai-review-loop](skills/ai-review-loop/SKILL.md) | 跟踪远程 AI 评审，处理反馈并重新验证 PR |
| [architecture-decision-record](skills/architecture-decision-record/SKILL.md) | 判断是否记录 ADR，并创建、更新或替代决策记录 |

### 写作与解释

| 技能 | 用途 |
| --- | --- |
| [technical-writing](skills/technical-writing/SKILL.md) | 起草或重构中文设计文档、源码分析和工程文章 |
| [style-aware-editor](skills/style-aware-editor/SKILL.md) | 清理 AI 套话与防御性表达，保留事实、文风和必要限定 |
| [eli5](skills/eli5/SKILL.md) | 用简单语言和图解解释复杂主题 |
| [show-me](skills/show-me/SKILL.md) | 可视化调用链、架构、数据流和状态变化 |
| [handoff](skills/handoff/SKILL.md) | 整理可接手的进展、决策、证据和剩余工作 |

### 技能与 Agent 配置

| 技能 | 用途 |
| --- | --- |
| [find-skills](skills/find-skills/SKILL.md) | 寻找和比较外部技能，判断是否适配 |
| [absorb-skill](skills/absorb-skill/SKILL.md) | 把外部资料中适用的规则合并进已有技能 |
| [skill-audit](skills/skill-audit/SKILL.md) | 审计技能规范、触发重叠、可移植性和评测 |
| [agent-health](skills/agent-health/SKILL.md) | 检查 Agent 指令、MCP、hooks、权限与配置漂移 |

### 专项分析

| 技能 | 用途 |
| --- | --- |
| [find-docs](skills/find-docs/SKILL.md) | 查询第三方库、框架、SDK、CLI 和 API 的官方文档 |
| [codecov-coverage](skills/codecov-coverage/SKILL.md) | 查询覆盖率，诊断 Codecov 检查失败 |
| [frontend-design-review](skills/frontend-design-review/SKILL.md) | 确定或审查前端视觉方向，并用截图或渲染验证 |
| [linux-performance-analysis](skills/linux-performance-analysis/SKILL.md) | 定位 Linux 主机或容器的性能瓶颈 |
| [supabase-postgres-best-practices](skills/supabase-postgres-best-practices/SKILL.md) | 根据查询计划和负载检查 Postgres 查询、索引、RLS 与配置 |
| [project-submission-evaluator](skills/project-submission-evaluator/SKILL.md) | 基于源码批量评审、评分和排序项目提交 |
| [x-tweet-fetcher](skills/x-tweet-fetcher/SKILL.md) | 获取研究所需的 X 推文、回复串、文章和中文社交平台内容 |

### 独立安装技能

需要本地有 Node.js 和 `npx`。以下命令只安装技能，无需运行仓库的环境初始化脚本：

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

部分技能使用 Claude Code/Codex 的扩展 frontmatter，或依赖同级 `_shared/` 规则；客户端兼容性和工具依赖见各自的 `SKILL.md`。第三方来源及许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。

Linux 的整套配置应用会跳过 `.agents`，需要技能时使用上面的独立安装命令。

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

## 环境安装

脚本需由 root 或具备 sudo 权限的用户通过 Bash 执行。非 root 用户先运行 `sudo -v`。Linux 会安装软件、配置系统并应用 dotfiles；macOS 会应用配置和安装 Shell 插件，Homebrew 清单需单独执行。

Linux 上存在 `sshd` 时，应用 SSH 安全配置要求目标用户的 `~/.ssh/authorized_keys` 非空，否则会停止。已部署的机器应先确认公钥登录可用；新用户可通过下方的 `GITHUB_USER` 导入公钥。

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
- 服务与系统：Docker 官方一键脚本（get.docker.com）、非 root 用户加入 docker 组、Tailscale、ZeroTier、IPv4/IPv6 转发、禁用 SSH 密码和交互式认证，以及 Fail2ban 配置。SSH 配置在重载前校验；Tailscale、ZeroTier 安装后仍需自行登录或加入网络，WSL 会跳过这两个工具；mihomo 只安装命令，不写入代理配置或启动服务。

默认不安装 glab、splitrail、Rust、Node、Go 开发工具、AI CLI、Kubernetes CLI、QEMU 和媒体处理工具。Linux 不下发桌面和 AI 配置；Neovim 使用系统包和默认配置，避免开发环境的插件自动下载工具链。已有软件不自动卸载。

`jd` 和 `uv` 安装到 `~/.local/bin`，`batcat`、`fdfind` 分别映射为 `bat`、`fd`。Python 是 httpie、pre-commit、fail2ban 等工具的依赖，`python3-systemd` 用于 fail2ban 读取 SSH 日志。可以设置 `GITHUB_TOKEN`，避免多个安装共用出口 IP 时触发 GitHub API 限流。

### 从本地仓库安装

如果已经克隆了仓库到本地：

```bash
./install.sh
```

### 安装参数与 Linux 用户

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

## 常用命令

```bash
chezmoi add ~/.zshrc --template

chezmoi diff

chezmoi apply -v
```

## Git worktree 辅助命令

`gwl` 列出当前仓库的 worktree，并查询本人最近 100 个 PR（含已关闭、已合并）。
优先匹配 `upstream`，再匹配 `origin`；没有 `upstream` 时，自动查询 fork 的上游仓库。
PR 的关联 Issue 会显示在 ISSUE 列；没有关联信息时，尝试从 `issue-<数字>` 分支查询。
找不到匹配 PR 或 GitHub 查询失败时，会在标准错误中提示。

实现位于 [home/dot_profile.d/git-worktree-helper](home/dot_profile.d/git-worktree-helper)。修改后可运行 `bash scripts/test-gwl.sh` 验证查询与回退行为。

## 开发与验证

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
[安装验证脚本](scripts/test-linux-install.sh) 在临时容器中使用官方 Debian 归档和最后一天的安全仓库快照：

```text
deb [check-valid-until=no] http://archive.debian.org/debian bullseye main
deb [check-valid-until=no] http://snapshot.debian.org/archive/debian-security/20260831T235959Z bullseye-security main
```

快照保留 Debian 签名校验，但不提供后续安全更新。参见 [Debian 官方仓库迁移讨论](https://lists.debian.org/debian-mirrors/2026/09/msg00001.html)。

## 进阶用法

- [使用私有和公开仓库管理配置](docs/private-public-repo-management.md)

### 更新 Homebrew 清单

在对应 macOS 环境中导出当前安装的软件，更新前后检查差异：

```bash
brew bundle dump --file=~/.local/share/chezmoi/home/Brewfile
```
