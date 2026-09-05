---
name: session-insights
description: 用户要求分析本地编程代理会话历史或生成 /insights 风格报告时使用，涵盖用量统计与工作流诊断。
---

# 会话洞察

根据本地编程代理会话文件生成 `/insights` 风格的使用报告。实现位于 `scripts/session_insights.py`，因此可将技能复制到任意项目，无需依赖 `claude-code` 源码树。

## 确定平台与范围

先从当前请求、先前已确认的上下文及用户指定路径解析以下两项；能唯一确定时直接使用。只有无法唯一确定平台或范围时，才询问缺失项；不要把未限定范围自动解释为 `all`。

1. 平台：
   - `claude`：Claude Code 会话。
   - `codex`：Codex 会话。
   - 其他工具：必须先在 `scripts/session_insights.py` 中增加解析适配器。
2. 范围：
   - `all`
   - 文件或目录路径
   - `recent:N`
   - `since:YYYY-MM-DD`
   - `project:TEXT`

将这两项作为技能参数：`[platform] [scope]`。

## 运行

在技能目录中执行：

```bash
python3 scripts/session_insights.py --platform <platform> --scope <scope>
```

默认进行工作流诊断。脚本会写入确定性指标，以及各会话的对话记录和分析产物；随后代理必须读取这些产物并补充语义分析。不要在脚本打印指标后就停止。

从项目根目录调用时，使用复制到项目中的技能路径：

```bash
python3 .claude/skills/session-insights/scripts/session_insights.py --platform claude --scope all
```

如果只需要确定性计数，显式关闭诊断：

```bash
python3 scripts/session_insights.py \
  --platform <platform> \
  --scope <scope> \
  --metrics-only
```

指定工作流产物目录：

```bash
python3 .claude/skills/session-insights/scripts/session_insights.py \
  --platform claude \
  --scope all \
  --export-dir /tmp/session-insights/claude-all
```

默认写入 `/tmp/session-insights/<timestamp>/`。使用 `--export-dir <dir>` 指定目录，使用 `--export-limit N` 限制导出的会话数。

## 当前适配器

- `claude`：扫描 `$CLAUDE_CONFIG_DIR/projects/*/*.jsonl` 或 `~/.claude/projects/*/*.jsonl`；重建 `uuid`/`parentUuid` 对话分支；移除 `/insights` 元会话；依据用户消息数和持续时间对分支会话去重。
- `codex`：扫描 `$CODEX_HOME/sessions/.../rollout-*.jsonl`、`$CODEX_HOME/archived_sessions/rollout-*.jsonl` 或 `~/.codex/...`；将 Codex JSONL 映射到相同的汇总结构。由于 Codex 事件结构不同于 Claude Code，目前只提供基础指标。

## 输出

脚本打印 Markdown 报告，并写入：

`<tool-home>/usage-data/session-insights-data.json`

Claude Code 的 `<tool-home>` 为 `$CLAUDE_CONFIG_DIR` 或 `~/.claude`。
Codex 的 `<tool-home>` 为 `$CODEX_HOME` 或 `~/.codex`。

默认的工作流诊断还会写入：

- `manifest.json`
- `session-insights-data.json`
- `analysis-instructions.md`
- `transcripts/*.md`
- `analyses/*.md`
- `workflow-summary.md`

代理完成语义分析后，还必须写入：

- `report.json`
- `report.html`

## 扩展约定

添加其他工具时，更新 `scripts/session_insights.py`：

1. 在 `platform_home()` 中添加平台。
2. 添加解析器，将该工具文件转换为类似 `SessionMeta` 的字典。
3. 在 `scan_sessions()` 中接入解析器。
4. 保持汇总和报告逻辑不变。

`SessionMeta` 必需字段：

- `session_id`
- `project_path`
- `start_time`
- `duration_minutes`
- `user_message_count`
- `assistant_message_count`
- `first_prompt`
- `source_file`
- `empty_stats()` 中的统计字段

## 语义维度

脚本计算确定性指标。目标、结果、满意度、帮助程度、会话类型、阻力和成功经验等章节，需要对对话记录进行语义分析。

不要在 `scripts/session_insights.py` 中硬编码工作流分类、建议或语义评分规则。脚本负责准备证据，AI 代理负责读取对话记录并分析。

默认工作流诊断步骤：

1. 正常运行脚本，可选用 `--export-dir`。
2. 阅读 `manifest.json`、`session-insights-data.json` 和 `analysis-instructions.md`。
3. 为 `transcripts/*.md` 中每份对话记录写入对应的 `analyses/*.md`。
4. 完成逐会话分析后，将反复出现的问题和建议汇总到 `workflow-summary.md`。
5. 写入包含结构化洞察章节的 `report.json`。
6. 将 `report.html` 写成易读的本地报告。
7. 除非结果来自官方工具，否则说明语义维度是代理生成的近似判断。

最终分析应提供可用于后续会话的新认识，包括：

- 概览：有效做法、阻碍、快速改进点和进阶工作流。
- 按对话证据归纳的工作主题，不套用固定分类。
- 成功经验和有效模式。
- 有证据支持的阻力点，并尽可能说明归因。
- 可直接粘贴且长期有效的 AGENTS.md 候选规则。
- 值得固化为可复用工作流的重复操作及技能候选。
- 用户可复制到未来 Codex 会话的提示词。
- 基于已观察行为提出的未来工作流。

对技能候选，提供建议名称、触发条件、重复原因、所需证据、核心步骤、验证方式和非目标。提出技能前，先判断重复行为更适合归入哪一类：

- AGENTS.md：简短且长期有效的行为规则。
- 技能：包含证据和验证的多步骤可复用工作流。
- 脚本：确定性的本地自动化。
- 记忆或文档：项目特定事实或以往决策。
- 无需固化：不应成为长期流程的一次性细节。

对话记录很多时，分批处理并将笔记保留在分析文件中。除非用户明确要求抽样，否则不要只分析极小样本。

## 验证

结束前：

1. 报告使用的平台和范围。
2. 报告 `total_sessions_scanned`、`raw_deduped_sessions` 和 `total_sessions`。
3. 确认 JSON 输出路径存在。
4. 除非使用了 `--metrics-only`，否则确认 `manifest.json`、`analysis-instructions.md`、`transcripts/`、`analyses/`、`workflow-summary.md`、`report.json` 和 `report.html` 均存在。
5. 说明哪些部分是确定性指标，哪些是近似判断。
