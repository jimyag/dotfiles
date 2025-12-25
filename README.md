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
