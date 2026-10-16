# 配置维护与本地验证

## 常用命令

```bash
chezmoi add ~/.zshrc --template

chezmoi diff

chezmoi apply -v
```

## Starship 提示符

配置位于 [home/dot_config/starship.toml](../home/dot_config/starship.toml)，沿用原 alanpeabody 的单行布局：紫色用户名和主机名、蓝色完整路径、括号内的绿色 Git 分支与状态，末尾为 `$`。右侧显示失败退出码和长命令耗时。

Starship 由 [zsh-prompt](../home/dot_profile.d/zsh-prompt) 初始化，oh-my-zsh 不再加载主题。现有自动建议、语法高亮、WakaTime 和补全缓存保持原有配置。

安装 Starship 后，可运行 `bash scripts/test-starship.sh` 检查非仓库、Git 分支、未提交修改、命令失败和 zsh 初始化。

## Node 版本与延迟加载

oh-my-zsh 的内置 `nvm` 插件启用延迟加载。启动 Shell 时只注册命令入口；首次运行 `node`、`npm`、`npx`、`pnpm`、`yarn`、`corepack`、`nvm`、`jd` 或清单中的 npm 命令时加载 NVM，并启用已有的默认 Node 版本。NVM 补全也在首次加载时初始化。

`nvm alias default` 查看默认版本；本配置不修改默认别名。项目内运行 `nvm use` 读取 `.nvmrc`，或用 `nvm use <版本>` 显式切换。未启用进入目录时自动切换版本。

Shell 初始化按职责分配：`.zshenv` 加载 Cargo 环境，`.zprofile` 加载登录环境，`common` 设置通用 PATH 和工具集成，`.zshrc` 统一扫描 `~/opt/*/bin`。补全缓存目录每次初始化只创建一次。

PATH 由 `.zshenv` 统一导出并去重，其他配置使用 zsh 的 `path` 数组添加目录。连续添加的目录按最终查找优先级合并，保留带空格的路径。

## 终端操作

- `Ctrl+R`：fzf 搜索历史命令；hstr 保留为 `hh`，不再绑定 Ctrl+R。
- `Ctrl+T`：fzf 搜索文件；`cd **<Tab>` 等写法触发模糊补全。
- `z` / `zi`：zoxide 目录跳转及交互选择。
- `ll` / `lt`：eza 详细列表和两层树形视图，`ls` 保留原有行为。
- `bat 文件`：语法高亮查看文件，`cat` 保留原有行为。
- `y`：打开 Yazi，正常退出后切到浏览的目录；`yazi` 直接启动则不改变 Shell 目录。

Ghostty 使用 12×8 内边距、透明原生标题栏、0.92 透明度和毛玻璃背景，退出后保存窗口布局。输入时隐藏鼠标；耗时至少 45 秒的命令结束且终端不在前台时发送桌面通知。通知使用 Ghostty 原生能力，Starship 只显示耗时，避免重复通知。窗口恢复不恢复正在运行的进程。

运行 `bash scripts/test-terminal-tools.sh` 检查快捷键、别名和 Yazi 的目录切换及失败处理。

## Git worktree 辅助命令

`gwl` 列出当前仓库的 worktree，并查询本人最近 100 个 PR（含已关闭、已合并）。
优先匹配 `upstream`，再匹配 `origin`；没有 `upstream` 时，自动查询 fork 的上游仓库。
PR 的关联 Issue 会显示在 ISSUE 列；没有关联信息时，尝试从 `issue-<数字>` 分支查询。
找不到匹配 PR 或 GitHub 查询失败时，会在标准错误中提示。

实现位于 [home/dot_profile.d/git-worktree-helper](../home/dot_profile.d/git-worktree-helper)。修改后可运行 `bash scripts/test-gwl.sh` 验证查询与回退行为。

## 本地验证

在仓库根目录逐个检查 Bash 脚本语法：

```bash
for script in install.sh scripts/*.sh skills/codecov-coverage/scripts/*.sh; do
  bash -n "$script"
done
```

在临时容器中运行安装入口（存在 `sshd` 时需先准备 SSH 公钥）：

```bash
docker run --rm -v "$PWD:/src:ro" debian:13-slim bash -c 'cp -a /src /tmp/dotfiles; bash /tmp/dotfiles/install.sh'
```

从本地仓库安装后，在仓库根目录使用 `chezmoi --source "$PWD/home" verify --exclude scripts` 检查文件是否与源配置一致，使用 `zsh -ic` 检查 Shell 加载。脚本由安装过程执行，文件校验时通过 `--exclude scripts` 排除。存在 `sshd` 时，用 `sshd -t` 检查配置语法；安装 Fail2ban 后，用 `fail2ban-client -t` 检查配置。

容器可验证软件安装和持久配置。服务启动、实时转发和 SSH 登录需在真实主机上验证；macOS 桌面应用的界面行为需人工验证。

## 更新软件清单

macOS 命令行工具在 `home/dot_config/jd/macos-tools` 和 `home/dot_config/jd/npm-tools` 中声明，由 jd 安装。Brewfile 保留应用和扩展，不用 `brew bundle dump` 覆盖，避免重新声明 jd 工具。

```bash
jd --installed
jd --upgrade
go-upgrade
```

公开与私有配置的同步方式见[使用私有和公开仓库管理配置](private-public-repo-management.md)。
