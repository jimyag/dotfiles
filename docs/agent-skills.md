# Agent Skills

技能按任务使用，点击名称可查看触发条件、流程和依赖。各技能的读写与授权规则见对应 `SKILL.md`。

### 开发与交付

| 技能 | 用途 |
| --- | --- |
| [brainstorming](../skills/brainstorming/SKILL.md) | 澄清目标、范围和关键假设，收敛实现方案 |
| [writing-plans](../skills/writing-plans/SKILL.md) | 为有多阶段依赖的实现编写执行计划 |
| [systematic-debugging](../skills/systematic-debugging/SKILL.md) | 用证据和最小复现定位缺陷、测试或构建失败 |
| [test-scenarios](../skills/test-scenarios/SKILL.md) | 整理测试计划、验收标准与 E2E 场景 |
| [runtime-verification](../skills/runtime-verification/SKILL.md) | 在真实运行面驱动改动并留存证据，交付前确认行为 |
| [requesting-code-review](../skills/requesting-code-review/SKILL.md) | 只读审查代码差异或 PR，检查正确性和复杂度 |
| [simplify](../skills/simplify/SKILL.md) | 保持行为不变，简化近期改动 |
| [git-commit](../skills/git-commit/SKILL.md) | 精准暂存并生成规范提交，按授权推送 |
| [pull-request](../skills/pull-request/SKILL.md) | 创建 PR，或整理标题、正文与模板 |
| [gh-stack](../skills/gh-stack/SKILL.md) | 管理相互依赖的分支和堆叠 PR |
| [loop-on-ci](../skills/loop-on-ci/SKILL.md) | 跟踪 Actions、修复失败并验证检查结果 |
| [architecture-decision-record](../skills/architecture-decision-record/SKILL.md) | 判断是否记录 ADR，并创建、更新或替代决策记录 |

### 写作与解释

| 技能 | 用途 |
| --- | --- |
| [technical-writing](../skills/technical-writing/SKILL.md) | 起草或重构中文设计文档、源码分析和工程文章；清理 AI 套话与防御性表达，保留事实、文风和必要限定 |
| [show-me](../skills/show-me/SKILL.md) | 可视化调用链、架构、数据流和状态变化，或用极简图解给外行讲原理 |

### 技能与 Agent 配置

| 技能 | 用途 |
| --- | --- |
| [absorb-skill](../skills/absorb-skill/SKILL.md) | 寻找和比较外部技能，把其中适用的规则合并进已有技能 |
| [agent-health](../skills/agent-health/SKILL.md) | 检查 Agent 指令、MCP、hooks、权限与配置漂移；审计技能规范、触发重叠、可移植性和评测 |
| [shared-memory](../skills/shared-memory/SKILL.md) | 整理并共享 Codex、Claude 的原生记忆，发现新来源并跟踪增量变化 |

### 专项分析

| 技能 | 用途 |
| --- | --- |
| [codecov-coverage](../skills/codecov-coverage/SKILL.md) | 查询覆盖率，诊断 Codecov 检查失败 |
| [frontend-design-review](../skills/frontend-design-review/SKILL.md) | 确定或审查前端视觉方向，并用截图或渲染验证 |
| [linux-performance-analysis](../skills/linux-performance-analysis/SKILL.md) | 定位 Linux 主机或容器的性能瓶颈 |
| [x-tweet-fetcher](../skills/x-tweet-fetcher/SKILL.md) | 获取研究所需的 X 推文、回复串、文章和中文社交平台内容 |

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

技能源码统一维护在根目录 `skills/`，使用上面的 `npx skills add` 命令安装。`home/dot_agents/skills` 的相对软链接供私有 Chezmoi 仓库同步源码；私有仓库已有脚本将各客户端的技能目录链接到 `~/.agents/skills/`。

部分技能使用 Claude Code/Codex 的扩展 frontmatter，或依赖同级 `_shared/` 规则；客户端兼容性和工具依赖见各自的 `SKILL.md`。第三方来源及许可证见 [THIRD_PARTY_NOTICES.md](../THIRD_PARTY_NOTICES.md)。

Linux 的整套配置应用会跳过 `.agents`，需要技能时使用上面的独立安装命令。
