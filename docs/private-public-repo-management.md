# 使用私有和公开仓库管理配置

## 为什么这样做

敏感配置较多且为文件级别（如私有 hosts、工作相关 alias），逐一存入密码管理器维护成本高。通过私有仓库存放敏感配置，公开仓库存放可分享配置。

## 目录结构

```plaintext
私有仓库 (主仓库)
├── .chezmoiroot            # 内容为 "home"
├── home/                   # 私有配置（优先级高）
│   └── dot_config/
├── public_dotfiles/        # 公开仓库 (git submodule)
│   └── home/               # 公开配置
└── scripts/
    └── sync_public_dotfiles.sh
```

- 私有仓库中已存在的文件不会被公开配置覆盖
- 公开配置通过软链接同步到私有仓库的 `home/` 目录

## 初始化设置

```bash
# 1. 创建私有仓库
mkdir my-private-dotfiles && cd my-private-dotfiles
git init

# 2. 配置 chezmoi root 目录
echo "home" > .chezmoiroot
mkdir home

# 3. 添加公开 dotfiles 仓库作为 submodule
git submodule add git@github.com:jimyag/dotfiles.git public_dotfiles

# 4. 复制同步脚本并运行
mkdir scripts
cp public_dotfiles/scripts/sync_public_dotfiles.sh scripts/
./scripts/sync_public_dotfiles.sh
```

## 在新机器上初始化

```bash
# 克隆私有仓库（会自动拉取 submodule）
git clone --recursive git@github.com:your/private-dotfiles.git

# 或者分步操作
git clone git@github.com:your/private-dotfiles.git
cd private-dotfiles
git submodule update --init --recursive

# 运行同步脚本
./scripts/sync_public_dotfiles.sh

# 应用配置
chezmoi init --source /path/to/private-dotfiles
chezmoi apply
```

## 日常使用

### 同步公开配置

```bash
./scripts/sync_public_dotfiles.sh
```

脚本会：

- 更新 submodule 到最新版本
- 为公开仓库的文件创建软链接
- 跳过私有仓库中已存在的文件
- 清理已删除的软链接

### 覆盖公开配置

在私有仓库的 `home/` 目录创建同名文件即可：

```bash
# 公开配置：public_dotfiles/home/dot_gitconfig
# 私有覆盖：home/dot_gitconfig（创建后公开配置被忽略）
```
