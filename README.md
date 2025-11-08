# dotfiles

## 一键安装

### 本地环境安装

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | sh
```

或者使用 wget：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | sh
```

### VPS 环境安装

在 VPS 上安装时，设置 `VPS=1` 环境变量以跳过某些开发工具的安装：

```bash
curl -fsSL https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | VPS=1 sh
```

或者：

```bash
wget -qO- https://raw.githubusercontent.com/jimyag/dotfiles/main/install.sh | VPS=1 sh
```

### 从本地仓库安装

如果已经克隆了仓库到本地：

```bash
# 本地安装
./install.sh

# VPS 安装
VPS=1 ./install.sh
```

## 手动安装

```bash
chezmoi init jimyag

# 本地环境
chezmoi apply -v

# VPS 环境
VPS=1 chezmoi apply -v
```

### 解决 chezmoi update 的 SSH 权限问题

如果在执行 `chezmoi update` 时遇到 `Permission denied (publickey)` 错误，这是因为 git 配置将 HTTPS URL 转换为 SSH。可以通过设置以下环境变量来使用 HTTPS：

```bash
export GIT_CONFIG_GLOBAL=/dev/null
export GIT_CONFIG_SYSTEM=/dev/null
export GIT_CONFIG_NOSYSTEM=1

# 然后执行 chezmoi update
chezmoi update
```

或者在一行中执行：

```bash
GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_SYSTEM=/dev/null GIT_CONFIG_NOSYSTEM=1 chezmoi update
```

**注意**：`install.sh` 脚本已经自动设置了这些环境变量，所以使用一键安装时不会遇到这个问题。

## 常用命令

```bash
chezmoi add ~/.zshrc --template

chezmoi diff

chezmoi apply -v
```

## 其他

```bash
brew bundle dump --file=~/.local/share/chezmoi/Brewfile
```
