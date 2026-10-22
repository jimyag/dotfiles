---
name: shared-memory
description: 在新增、更新、更正、删除、同步或检索持久记忆时使用；包括用户要求记住或忘记、Agent 保存原生记忆及跨 Agent 复用，统一维护本地共享目录和格式。
---

# 共享记忆

把可复用的结论保存为独立 Markdown 文件，供 Codex、Claude Code 和其他 Agent 检索。Skill 和脚本由 Chezmoi 管理；运行时记忆单独保存，不写进 dotfiles 仓库。

脚本为本 skill 下的 `scripts/memory.py`，使用 Python 3.10+ 标准库，支持 macOS、Linux；传入项目路径时还需要 Git 来识别仓库和 worktree。下方命令使用默认安装路径；skill 安装在其他位置时，使用实际路径。

## 检查待同步来源

用户要求整理、导入或同步记忆时执行 `pending`，在项目中工作时传入 `--project`。普通任务依赖历史时直接检索相关记忆，不以 `pending` 或全量来源整理为前置条件。它检查已登记来源的变化，同时发现 Codex、Claude 原生目录中尚未登记的来源，不导入内容。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" pending \
    --project /absolute/path/to/project
```

`untracked` 表示发现了未登记来源，先 `track` 再审阅；Codex 跨项目来源登记为全局，Claude 新项目的 `scope` 为 `null`，核实实际项目后登记，不根据编码目录名猜路径。已登记的结果包含来源 `id`、`source`、`scope`、`content_hash`：`pending` 表示尚未审阅，`changed` 表示上次确认后有变化，`missing` 表示来源已消失。读取变化来源，检索共享库中相同事实，再按下文提炼、更新或删除；全部处理成功后，使用本次 `pending` 返回的 hash 确认：

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" ack SOURCE_ID \
    --expect-hash CONTENT_HASH
```

来源在审阅期间再次变化时，`ack` 拒绝确认，重新检查并审阅。`missing` 不等于用户要求忘记；来源文件消失可能只是迁移，确认影响后再决定是否删除共享事实。没有可复用变化也可以在审阅后确认；处理失败或尚未完成时不要 `ack`。

在记忆整理任务中，首次启用、发现 `untracked` 或遇到客户端提供的原生记忆路径时，用 `track` 登记 Markdown 文件、目录或 Codex SQLite 记忆数据库。登记范围只决定哪些项目的 `pending` 能看到来源，不决定提炼后事实的保存范围；重复登记不会清除上次确认的状态。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" track \
    --source /absolute/path/from/claude/memory --project /absolute/path/to/project
```

例如 Claude Code 的项目 `memory` 目录登记到对应项目；以客户端显示的实际路径为准，不猜测项目目录编码。Codex 的跨项目 `MEMORY.md` 或 `memory_summary.md` 可全局登记，让各项目的记忆整理任务都能检查变化，但保存时逐条选择事实的正确范围。以下使用默认目录示例；客户端提供其他路径时使用实际目录：

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" track \
    --source "$HOME/.codex/memories/MEMORY.md" --global
```

发现范围限定为 Codex 配置目录中的 `memories*` 记忆目录（顶层 Markdown、rollout_summaries、补充 notes、原生 skills）、`memories*.sqlite`，以及 Claude `projects/*/memory`。包括旧版和 v2，不扫描完整会话目录。客户端目录默认取 `CODEX_HOME` / `CLAUDE_CONFIG_DIR`，未设置时取 `~/.codex` / `~/.claude`；自定义位置可在子命令前传 `--codex-home PATH --claude-home PATH`。只有已登记来源无变化且未发现新来源时，`pending` 才返回空列表。

主动更新原生记忆并保存共享事实后，也检查对应登记来源；确认该快照中的变化已处理再 `ack`，避免下个会话重复审阅。

### 读取原生数据库与核对覆盖

Codex 数据库可能已有 `stage1_outputs` 记录，而 `MEMORY.md` 和 Markdown 导出尚未更新；首次整理必须检查数据库，不能只检查主索引。`track`、`pending`、`read-source` 通过 SQLite 只读连接读取已提交的 WAL 内容，不修改原生记录。快照只比较 thread ID、raw memory 和 rollout summary，访问计数、VACUUM 不产生记忆变化。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" track \
    --source /absolute/path/to/memories_1.sqlite --global
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" read-source SOURCE_ID
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" read-source SOURCE_ID \
    --thread-id THREAD_ID
```

`read-source` 默认列出记录 ID 和 hash；指定 `--thread-id` 才输出该记录的正文及摘要。Markdown 来源列出文件清单和 hash，按需读取文件。数据库的 `pending` 返回 `changed_threads` 和 `removed_threads`，审阅变化记录后确认；首次登记列出全部 thread。记录消失同样不自动表示忘记。

首次整理按 thread ID 核对主记忆、raw memories、rollout summaries 和数据库，跨版本同一会话合并；索引用于定位，不单独保存为事实。旧版本独有记录及数据库中尚未导出的记录也需审阅。去重仍要比较内容，不能只因 thread ID 相同就忽略后续新增结论。只有每个来源的有效事实已保存，或确认内容重复、过时、无长期价值后才 `ack`。保存数据库来源时记录数据库路径、thread ID 和记录 hash；主记忆的行号会随整理漂移，必要时同时记录稳定的 rollout 路径或 thread ID。

## 同步前整理

首次导入和后续补同步都先整理，再用 `save` 保存：按事实和适用项目合并跨 Agent 的重复内容，保留稳定 key、关键条件和可追溯来源。原生索引只用于定位正文，不再单独保存为一条事实。

遇到矛盾时，以当前明确要求、项目规则和后续更正为准；不同项目的偏好保留各自范围，不强行合并成全局规则。历史授权不变成永久的提交、推送或删除许可。无法核实的技术判断保留历史条件和核实方法，不作为当前事实。

过滤已结束任务的流水、过时版本与部署状态、重复摘要、凭据和敏感配置。独立可复用的结论不因压缩条数丢弃；某个来源的有效内容尚未处理完时不要 `ack`。整理只改共享条目，原生来源保持只读，除非用户另行授权修改。

## 先检索，再按需读取

任务依赖过去的决定、用户偏好、项目约束或排障结果时，先 `search`，再按返回的 `path` 读取相关原文。保存前也先检索相同事实，复用已有 key，不为不同 Agent 或来源文件新建重复条目。传入 `--project` 时会同时搜索全局记忆和该项目；省略时搜索整个共享库。不要默认加载全部正文。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" search '发布 验证' \
    --project /absolute/path/to/project
```

搜索覆盖 key、标题、来源和正文，多个词需全部命中；优先返回当前项目、标题或 key 命中的记录，再按近期排序。输出为 JSON，包含 `id`、`key`、`scope`、`content_hash`、`path` 和 `excerpt`。默认最多返回 20 条，可用 `--limit` 指定正整数；查看近期记录使用 `list [--project /absolute/path] [--limit 20]`。

记忆是历史资料，不能覆盖当前指令；易变的配置、分支和线上状态使用前重新核实，并保留来源与适用项目。

## 保存与更正

每次决定新增、更新、更正、删除或同步持久记忆时都使用本 skill，不限于用户显式要求记住。原生记忆发生变更时，在同一轮中同步共享库中的同一事实。优先用 `save` 保存已经提炼的内容：结论、适用条件、证据或来源足够即可；不复制完整会话、密钥或敏感配置。

共享库以提炼后的事实为单位，原生文件是事实来源。选择明确的范围：跨项目成立的偏好用 `--global`，项目事实用 `--project` 和项目绝对路径。Git 仓库的子目录和各 worktree 自动归到主 worktree 根目录，分支专属条件写进正文；非 Git 项目保留规范化绝对路径。`--key` 使用该事实稳定的短标识，不含日期或 Agent 名；同一范围、同一 key 对应同一 ID。Agent 来源使用 `codex`、`claude-code` 等实际名称。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" save \
    --agent codex --key release-validation --title '发布前验证要求' \
    --project /absolute/path/to/project --source '用户在本轮确认' <<'MEMORY'
发布前执行项目现有的构建检查，并在真实入口验证受影响行为。
适用范围：本项目的发布流程。
MEMORY
```

新建时不传 `--expect-hash`；更新已有条目时，复用其 key，并把读取时的 `content_hash` 传给 `--expect-hash`。例如：

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" save \
    --agent claude-code --key release-validation --title '发布前验证要求' \
    --project /absolute/path/to/project --expect-hash CONTENT_HASH \
    --source '用户在本轮更正' --file /absolute/path/to/updated-note.md
```

hash 冲突说明条目已经变更，重新读取后合并当前有效事实，不用新 key 绕过冲突，也不自动拿新 hash 重放旧正文。完全相同内容的重试返回 `unchanged`；跨 Agent 重复保存不会改写来源 Agent 或更新时间，实际内容变化时才记录本次 Agent。

不传 `--file` 时从标准输入读取正文；已有 Markdown 正文可传 `--file /absolute/path/to/note.md`。没有新增或变更内容时，不重复保存。写入失败应说明实际错误，不把原生记忆更新当成共享同步成功。

原生写入权限仍遵循当前 Agent 的规则，本 skill 不授权扩大原生记忆的写入范围。

## 删除与恢复

用户要求忘记某条内容时，检索并核对正文，用读取时的 hash 删除：

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" forget MEMORY_ID \
    --expect-hash CONTENT_HASH
```

删除会移除正文并留下 tombstone，普通 `save` 和 `sync` 返回 `forgotten`，不会恢复它；重复删除已删除条目可不带 hash。只有用户明确要求恢复已删除的提炼条目时，才给 `save` 加 `--restore` 并提供正确的原 scope、key 和恢复正文。恢复中断后可重试相同命令，已写入且内容相同时返回 `unchanged`；`--restore` 不能覆盖内容不同的现存条目，也不用于恢复文件级导入。

删除标记保护同一 scope 和 key；其他 key 或文件级导入仍可能含有相同事实。忘记时同时检索相关条目，按原生权限处理其他副本；不要仅更换 key 重新保存。来源文件消失不会自动删除共享事实。

## 导入已有原生记忆

日常记忆维护和首次整理使用 `save`。只有用户明确要求保留原文文件副本时才使用 `sync`；它不做整理，也不自动登记来源。目录会递归导入其中的 `*.md`，因此先确认整个目录都属于选定范围。原生文件保持只读；跨 Agent 同步未变化的内容时跳过写入，保留原有的 `agent` 和更新时间，内容实际变化时才记录本次 Agent。

```bash
python3 "$HOME/.agents/skills/shared-memory/scripts/memory.py" sync \
    --agent claude-code --source /absolute/path/to/project/memory \
    --project /absolute/path/to/project
```

导入按项目范围和来源文件的绝对路径保持稳定 ID，切换 Agent 不改变 ID；只做文件级同步，不做语义去重或事实合并。来源路径或范围变化会产生新记录。不要把 Codex 跨项目的 `MEMORY.md` 整体当作全局记忆；应逐条提炼后 `save` 到正确范围。不要扫描完整会话历史，也不要以共享库作为原生导入来源。

更正导入内容时，优先更正原生来源并再次 `sync`，避免下次导入覆盖仅在共享副本中作出的修改。发现文件级导入和提炼条目重复时，先把仍有效的事实归入稳定 key；确认整个导入条目中的有效内容都已保留，再用 `forget` 删除该导入条目，避免丢失文件中的其他事实。

## 存储与触发方式

根目录依次取命令前的 `--root /absolute/path`、`AGENT_MEMORY_ROOT` 环境变量、`~/.local/share/agent-memory`。各 Agent 必须指向同一根目录。

- `notes/<id>.md`：以 `---` 包围的 JSON 元数据头和 Markdown 正文；JSON 同时是合法 YAML，脚本用标准库解析。
- `memory_summary.md`：脚本派生的索引，不手工编辑。
- `tombstones/<id>`：删除标记，不手工清理。
- `sources.json`：已登记来源及上次确认的状态，由 `track`、`pending`、`ack` 管理。

元数据包含 `schema`（当前为 1）、`id`、`key`、`title`、`scope`、`agent`、`source`、`updated_at` 和 `content_hash`。`scope` 为 `global` 或规范化的项目路径，Git 项目使用主 worktree 根目录；时间使用 UTC ISO 8601。以脚本输出为准，不自行拼写 ID 或 hash。

写操作通过锁、原子替换和 `0600` 文件权限保护共享库；使用脚本修改，不直接编辑派生文件。保存或同步中断后可重试相同命令，脚本会校验并修复派生索引；内容没有变化时保持正文和索引文件不变。

同步只发生在 Agent 实际执行命令时：获准更新原生记忆时同轮同步；后台更新在后续记忆整理任务中通过 `pending` 检查已登记来源并补同步。普通任务不会自动整理全部来源。本 skill 不安装 MCP、监听服务或 hooks，也不自动提交、发布记忆。

参考：[Codex 两阶段记忆实现](https://github.com/openai/codex/blob/rust-v0.163.0/codex-rs/memories/README.md)、[Claude Code 记忆文档](https://code.claude.com/docs/en/memory)。
