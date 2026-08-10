# dotfiles

这是我的个人 dotfiles 仓库，里面有一些写死的个人配置，例如默认仓库 `jimyag/dotfiles`、默认 `chezmoi init jimyag`、Git 用户信息、邮箱和部分脚本提示。直接使用前建议先通读并替换为自己的值。

## Agent Skills

`home/dot_agents/skills/` 包含可复用的 Agent Skills。它们会通过 Chezmoi
应用到 `~/.agents/skills/`，也可以单独复制到兼容 Agent Skills 的客户端。

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

### 本地环境安装

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | bash
```

### VPS 环境安装

在 VPS 上安装时，设置 `VPS=1` 环境变量以跳过某些开发工具的安装：

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | VPS=1 bash
```

或者：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | VPS=1 bash
```

### 从本地仓库安装

如果已经克隆了仓库到本地：

```bash
# 本地安装
./install.sh

# VPS 安装
VPS=1 ./install.sh
```

### Linux 上创建用户并配置 SSH

脚本需由具备 sudo 权限的用户执行。在 Linux VPS 上可通过环境变量创建带 sudo 的用户，并将指定 GitHub 用户的公钥写入其 `~/.ssh/authorized_keys`（仅 Linux，macOS 不创建用户）：

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

# 本地环境
chezmoi apply -v

# VPS 环境
VPS=1 chezmoi apply -v
```

## 常用命令

```bash
chezmoi add ~/.zshrc --template

chezmoi diff

chezmoi apply -v
```

## 进阶用法

- [使用私有和公开仓库管理配置](docs/private-public-repo-management.md)

## 其他

```bash
brew bundle dump --file=~/.local/share/chezmoi/Brewfile
```
