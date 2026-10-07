# dotfiles

我的个人 dotfiles、环境初始化脚本和 Agent Skills，由 Chezmoi 管理。可以单独安装技能，也可以使用整套配置初始化 macOS 或 Linux 环境。

## 仓库功能

- Shell 与 Git：zsh、oh-my-zsh 插件、别名、函数和 Git 配置；`gwl` 可查看 worktree 及关联的 GitHub PR。
- macOS 配置：Homebrew 软件清单、Neovim、Ghostty、Kitty、Zellij 和 Hammerspoon 配置。
- Linux 初始化：安装命令行工具、Docker 和网络工具，配置 SSH 公钥认证、Fail2ban 与 IP 转发；可创建用户、导入 GitHub 公钥和设置主机名。
- Agent Skills：需求澄清、调试、评审、GitHub 交付、技术写作、技能维护和专项分析。

整套配置包含个人 Git 身份、默认仓库和应用偏好。环境初始化会安装软件并修改配置，使用前请阅读[安装与复用说明](docs/installation.md)。

## Agent Skills

需要本地有 Node.js 和 `npx`，可查看或安装技能：

```bash
npx skills add jimyag/dotfiles --list
npx skills add jimyag/dotfiles --skill systematic-debugging
```

[技能目录](docs/agent-skills.md)列出全部 30 个技能的用途、安装方式及客户端兼容性说明。

## 使用文档

| 文档 | 内容 |
| --- | --- |
| [Agent Skills](docs/agent-skills.md) | 按任务选择和安装技能 |
| [安装与复用](docs/installation.md) | 平台行为、安装清单、参数、SSH 前置条件和个人配置替换 |
| [配置维护与本地验证](docs/maintenance.md) | Chezmoi 常用命令、`gwl`、安装检查和 Brewfile 更新 |
| [公开与私有配置管理](docs/private-public-repo-management.md) | 通过子模块和软链接维护可分享配置与敏感配置 |

## 目录

| 路径 | 内容 |
| --- | --- |
| [skills/](skills/) | 可独立安装的技能、参考资料、脚本和评测场景 |
| [home/](home/) | Chezmoi 配置，`dot_` 映射为点文件，`.tmpl` 表示模板 |
| [home/.chezmoiscripts/](home/.chezmoiscripts/) | 随 Chezmoi 应用执行的安装与系统配置脚本 |
| [home/Brewfile](home/Brewfile) | macOS 软件和开发工具清单 |
| [install.sh](install.sh) | 环境初始化入口 |
| [scripts/](scripts/) | 配置同步和辅助脚本 |

第三方来源及许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)，仓库许可证见 [LICENSE](LICENSE)。
