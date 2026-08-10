---
name: agent-health
description: 在需要检查 Codex/Claude/agent 配置、AGENTS.md、skills、hooks、MCP、验证命令或 AI 工作流是否漂移时使用。适用于 dotfiles、agent 配置仓库和长期项目的健康审计。
---

# Agent 配置健康检查

## 目标

找出 agent 工作流里会让后续执行变差的配置漂移：规则冲突、skill 触发错误、hooks 过宽、MCP 权限不清、验证命令失真、持久上下文过期。

## 何时使用

- 检查 `AGENTS.md`、`CLAUDE.md`、skills、hooks、MCP、agent config
- 用户觉得 Codex/Claude 没按规则执行
- 新增或迁移一批 skills 后，需要确认边界是否清楚
- 长期项目里验证命令、生成物规则或上下文文档可能已经过期

## 审计层次

按下面顺序检查，先做概要检查，只有发现高风险或用户要求深入时再扩展：

1. `指令入口`：`AGENTS.md`、`CLAUDE.md`、项目 README、skill frontmatter 是否冲突
2. `Skill 路由`：description/when_to_use 是否过宽、互相抢触发、缺少禁用边界
3. `工具与 hooks`：hooks、MCP、allowed tools、脚本是否有过宽权限或隐式副作用
4. `验证入口`：测试、lint、build、apply、生成物检查是否真实可运行
5. `持久上下文`：计划、handoff、memory、docs 是否过期、重复或包含私有路径
6. `可维护性`：是否有重复规则、薄 skill、无人维护的脚本、公共/私有边界混乱

## 检查规则

- 证据优先：每个问题必须引用具体文件、命令输出或配置项
- 当前仓库状态优先于记忆和旧总结
- 不把缺少“完美治理”当问题；按项目复杂度校准
- hooks 和自动触发规则要重点看副作用、权限范围和是否可关闭
- 发现敏感信息时只报告类型和路径，不复制具体值

## 输出格式

```text
## Agent 健康检查

问题：
- [P0/P1/P2] <问题> - <文件或配置>
  证据：...
  影响：...
  处理：...

正常区域：
- ...

残余风险：
- ...
```

## 严重度

- `P0`：会泄露敏感信息、自动执行破坏性动作、错误发布/提交/部署
- `P1`：会持续误导 agent，例如错误验证命令、过宽触发、冲突规则、失效 hooks
- `P2`：维护成本或清晰度问题，例如重复规则、过期文档、低价值 skill
