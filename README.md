# dotfiles

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
| `CREATE_USER` | 要创建的用户名，默认为 `jimyag`；设为非空时在 Linux 上执行创建用户和/或更新 SSH 授权 |
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
