---
name: handoff
description: 在长任务需要交接、上下文即将压缩、准备换线程/换 agent、或用户要求整理当前进展时使用。适用于把事实、决策、剩余工作和建议后续 skill 压缩成可继续执行的交接说明。
---

# 任务交接

## 目标

把当前工作整理成下一位 agent 或下一轮对话能直接接手的状态。
重点保留事实、路径、命令结果、未完成项和风险，不复制完整聊天记录。

## 何时使用

- 用户要求整理当前进展或生成交接说明
- 长任务已经跨多个阶段，后续需要继续执行
- 上下文即将压缩，需要避免丢失关键事实
- 需要把当前线程的结果交给另一个线程、agent 或人工继续

## 何时不要使用

- 任务很短，最终回复已经足够说明状态
- 用户只是要 commit、push、PR 文案或代码 review
- 交接内容会泄露密钥、token、私钥或敏感配置值

## 交接内容

按需包含这些部分：

- `Goal`：用户原始目标和当前目标是否发生变化
- `Current State`：已经完成什么，哪些文件/仓库/分支受影响
- `Decisions`：已经做出的关键判断，特别是用户明确拍板的范围边界
- `Evidence`：重要命令、测试、日志、链接或输出结论；只写结论和可复跑命令
- `Dirty State`：未提交改动、未 push commit、运行中的服务或临时文件
- `Persistent Files`：若存在 `task_plan.md`、`findings.md`、`progress.md`、PRD、issue 或设计文档，列出路径和当前权威来源
- `Remaining Work`：下一步最小可执行动作
- `Risks`：未验证、需要用户确认、可能过期或依赖外部状态的内容
- `Suggested Skills`：下一轮最可能需要用到的 skill，例如 `systematic-debugging`、`requesting-code-review`、`git-commit`

## 写法要求

- 用短句和具体路径，不写泛泛总结
- 明确区分事实、推断和待确认事项
- 保留能继续执行的命令，但不要堆完整日志
- 不重复已经存在的 PR body、计划文档或 changelog，只引用路径或链接
- 不写“已经完成”除非有当前验证证据

## 安全约束

- 不复制 token、私钥、cookie、一次性验证码、内部密码
- 如果命令输出包含敏感值，只写“已确认存在/缺失/匹配”，不要贴原值
- 对可能过期的外部状态标注检查时间或说明需要重新验证

## 输出模板

```text
## Handoff

Goal:
- ...

Current State:
- ...

Decisions:
- ...

Evidence:
- ...

Dirty State:
- ...

Persistent Files:
- ...

Remaining Work:
- ...

Risks:
- ...

Suggested Skills:
- ...
```
