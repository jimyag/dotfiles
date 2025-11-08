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

如果在执行 `chezmoi update` 时遇到 `Permission denied (publickey)` 错误，这是因为 git 配置将 HTTPS URL 转换为 SSH。

**推荐方式**：使用 `chezmoiu` 函数（chezmoi update 的快捷方式，已自动配置 HTTPS）：

```bash
chezmoiu
```

或者手动设置环境变量：

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

**注意**：

- `install.sh` 脚本已经自动设置了这些环境变量，所以使用一键安装时不会遇到这个问题
- `chezmoiu` 函数在配置加载后可用，会自动处理这些环境变量

## 在私有仓库中引用此配置

如果你有一个私有仓库（如 `p-dotfiles`）需要引用这个公开配置，可以使用以下方法：

### 方法 1：使用 Git Submodule（推荐）

在私有仓库中添加此仓库作为子模块：

```bash
cd ~/path/to/p-dotfiles
git submodule add https://github.com/jimyag/dotfiles.git public-dotfiles
```

然后创建一个合并脚本 `merge-sources.sh`：

```bash
#!/bin/bash
# 合并公开配置和私有配置
PUBLIC_DIR="public-dotfiles"
PRIVATE_DIR="."

# 复制公开配置到临时目录
TMP_DIR=$(mktemp -d)
cp -r "$PUBLIC_DIR/home" "$TMP_DIR/"
cp -r "$PUBLIC_DIR/.chezmoiscripts" "$TMP_DIR/" 2>/dev/null || true

# 合并私有配置（私有配置优先）
if [ -d "$PRIVATE_DIR/home" ]; then
  cp -r "$PRIVATE_DIR/home"/* "$TMP_DIR/home/" 2>/dev/null || true
fi
if [ -d "$PRIVATE_DIR/.chezmoiscripts" ]; then
  cp -r "$PRIVATE_DIR/.chezmoiscripts"/* "$TMP_DIR/.chezmoiscripts/" 2>/dev/null || true
fi

# 使用合并后的配置初始化 chezmoi
chezmoi init --apply --source="$TMP_DIR"
rm -rf "$TMP_DIR"
```

### 方法 2：使用符号链接

在私有仓库中创建符号链接：

```bash
cd ~/path/to/p-dotfiles
git submodule add https://github.com/jimyag/dotfiles.git public-dotfiles

# 创建符号链接（私有配置优先）
ln -s ../public-dotfiles/home public-home
ln -s ../public-dotfiles/.chezmoiscripts public-scripts

# 在私有仓库中只存放私有配置
# 使用脚本合并两个目录
```

### 方法 3：使用脚本自动合并

创建一个 `apply.sh` 脚本在私有仓库中：

```bash
#!/bin/bash
set -e

PUBLIC_REPO="https://github.com/jimyag/dotfiles.git"
PUBLIC_DIR=".public-dotfiles"
PRIVATE_DIR="."

# 克隆或更新公开仓库
if [ ! -d "$PUBLIC_DIR" ]; then
  git clone "$PUBLIC_REPO" "$PUBLIC_DIR"
else
  cd "$PUBLIC_DIR"
  git pull
  cd ..
fi

# 创建合并后的源目录
MERGED_DIR=".merged-source"
rm -rf "$MERGED_DIR"
mkdir -p "$MERGED_DIR"

# 先复制公开配置
cp -r "$PUBLIC_DIR/home" "$MERGED_DIR/" 2>/dev/null || true
if [ -d "$PUBLIC_DIR/.chezmoiscripts" ]; then
  cp -r "$PUBLIC_DIR/.chezmoiscripts" "$MERGED_DIR/" 2>/dev/null || true
fi

# 再合并私有配置（覆盖公开配置）
if [ -d "$PRIVATE_DIR/home" ]; then
  cp -r "$PRIVATE_DIR/home"/* "$MERGED_DIR/home/" 2>/dev/null || true
fi
if [ -d "$PRIVATE_DIR/.chezmoiscripts" ]; then
  mkdir -p "$MERGED_DIR/.chezmoiscripts"
  cp -r "$PRIVATE_DIR/.chezmoiscripts"/* "$MERGED_DIR/.chezmoiscripts/" 2>/dev/null || true
fi

# 应用配置
chezmoi init --apply --source="$MERGED_DIR"
```

**推荐使用方法 1（Git Submodule）**，因为它：
- 保持两个仓库的独立性
- 易于更新公开配置
- 版本控制清晰

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
