# 配置维护与本地验证

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

## 更新 Homebrew 清单

在对应 macOS 环境中导出当前安装的软件，更新前后检查差异：

```bash
brew bundle dump --file="$(chezmoi source-path)/Brewfile"
```

公开与私有配置的同步方式见[使用私有和公开仓库管理配置](private-public-repo-management.md)。
