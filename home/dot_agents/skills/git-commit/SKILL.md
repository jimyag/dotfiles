---
name: git-commit
description: 在用户明确要求创建 commit、生成 commit message、或 push 当前改动时使用。适用于当前改动已经完成并准备提交的场景。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards and argument hints, plus git and network access when pushing.
when_to_use: 当前改动已经完成，工作区里有待提交内容，用户明确要求创建 commit、生成 commit message 或 push 当前分支。
disable-model-invocation: true
argument-hint: "[context]"
allowed-tools: >-
  Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*)
  Bash(git log:*) Bash(git status:*) Bash(git push:*)
---

# 规范化提交

开始时声明："我正在使用 git-commit skill 生成并提交规范化 commit。"

## 快速开始

1. 查看 `status/diff/log`，确认提交范围与语言风格。
2. 暂存目标文件并展示“将提交列表”。
3. 生成符合 Angular 规范的 commit message。
4. 用户只要 commit message 时输出草案并停止，不暂存、commit 或 push。

## 预检查命令

```bash
git status --short
git diff HEAD
git branch --show-current
git log --oneline -10
```

## 消息规范

Header：`<type>(<scope>): <summary>`

Type：
- `feat` 新功能
- `fix` 缺陷修复
- `docs` 文档改动
- `refactor` 重构
- `perf` 性能优化
- `test` 测试相关
- `build` 构建系统或依赖
- `ci` CI 配置/脚本
- `chore` 杂项维护

Summary 规则：祈使句、现在时、首字母小写、不加句号。

Body 规则：
- `docs` 可省略，其他类型建议必须有
- 至少说明“为什么改”与“影响范围”
- 非 `docs` 类型时，body 至少 20 个字符
- 单段 body 不超过 3 行，保持简洁

Footer（按需）：
- `BREAKING CHANGE: ...`
- `DEPRECATED: ...`
- `Fixes #123` / `Closes #456`

## 语言规则

- 参考最近 10 条提交语言。
- 近期中文为主则用中文；近期英文为主则用英文。

## 执行流程

1. 先确认提交文件列表。
2. 生成并复核 commit message 草案。如果用户只要求生成 message，输出草案后停止。
3. 用户明确要求执行 commit 时，执行 `git add`；该请求已满足提交确认，不再重复等待。
4. 执行 `git commit -s`（必须带 sign-off 标志）。

## 参数规则

- 所有参数都视为上下文字符串，用于辅助生成 commit message。

## 关键约束

- 必须使用 `-s` 标志进行 sign-off，示例：`git commit -s -m "message"`
- 不要使用 emoji 在 commit message 中

## 输出边界

- 只生成 message 时输出 `Push: 未执行`。

## 输出模板

只生成 message：

```text
标题: <type(scope): summary>
正文: <body 或 "无">
已提交: 否
Push: 未执行
```

执行 commit：

```text
已提交: <commit-hash>
标题: <type(scope): summary>
分支: <branch>
```

## 失败回退

- 工作区无变更：输出 `git status` 结果，提示无可提交内容。
- `git commit` 失败（hook 报错）：输出完整报错，建议修复后重试，不跳过 hook。
- `git push` 失败（远端冲突）：输出报错，建议先 pull/rebase 再重试。

## 统一约束

- 验收标准：遵循 `skills/_shared/common-acceptance.md`
- 系统规范：遵循 `home/dot_agents/AGENTS.md`
- 本 skill 的额外约束：commit 必须带 sign-off；commit message 不使用 emoji。

## 参考资料

- [Angular Commit Message Guidelines](https://github.com/angular/angular/blob/main/contributing-docs/commit-message-guidelines.md)
