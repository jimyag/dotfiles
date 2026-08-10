---
name: using-superpowers
description: 在开始处理任何用户请求时使用，用于先判断当前任务是否需要启用某个 skill，再决定后续执行方式。适用于需要在直接动手前先做 skill 选择的场景。
compatibility: Local Claude/Codex routing profile; requires client support for hiding routing-only skills from user invocation.
when_to_use: 新任务开始时、任务类型发生切换时，或一个请求同时像多个 workflow，需要先路由到合适的 skill 再继续执行。
user-invocable: false
---

# 选择并使用 Skill

按以下顺序选择最小必要 skill：

1. 用户明确点名的 skill。
2. 与当前目标明显匹配的 skill。
3. 没有明显匹配时直接执行，不为简单任务增加流程。

请求同时匹配多个 workflow 时，读取 [触发优先级矩阵](../_shared/trigger-priority-matrix.md)；行动前用 [跨 Skill 反模式](../_shared/anti-patterns.md) 检查是否扩大了用户授权范围。

用户指令和当前目录生效的 `AGENTS.md` 高于 skill 默认流程。任务从分析切换到实现、提交、PR、CI 或发布时，重新判断一次 skill，不沿用上一阶段的选择。
