---
name: git-commit
description: 在用户明确要求生成 commit message、创建 signed-off commit，或提交后 push 当前分支时使用。根据真实 diff 精准暂存并生成 Conventional Commit；只要求 message 时不修改仓库，push 只在明确要求时执行。
compatibility: Requires git. Push requires network access and an authenticated remote.
allowed-tools: Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*) Bash(git log:*) Bash(git status:*) Bash(git push:*)
---

# 创建规范化提交

## 边界

- 用户只要 commit message：输出草案，不暂存、不提交、不 push。
- 用户要求 commit：检查并精准暂存目标文件，执行提交，不默认 push。
- 只有用户明确要求 push 时才 push。
- 保留工作区中与本次任务无关的改动，不使用 `git add .` 代替范围判断。

## 流程

1. 确认目标仓库和当前状态：

   ```bash
   git rev-parse --git-dir
   git status --short
   git diff HEAD
   git branch --show-current
   git log --oneline -10
   ```

2. 根据用户授权和 diff 确定提交范围；混有无关改动时只暂存目标路径。
3. 根据仓库近期惯例生成 `<type>(<scope>): <summary>`：
   - `feat`、`fix`、`docs`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`
   - summary 使用祈使语气、现在时，不加句号或 emoji
   - body 解释为什么改和影响范围；简单文档提交可省略
   - 按需加入 `BREAKING CHANGE:`、`DEPRECATED:`、`Fixes #123` 或 `Closes #123`
4. 暂存后再次检查：

   ```bash
   git diff --cached --stat
   git diff --cached
   ```

5. 执行 `git commit -s`。`-s` 是必需的 sign-off，不得省略或用配置猜测替代。
6. 读取新 commit 的 hash 和 summary。用户同时明确要求 push 时，再 push 当前分支；无 upstream 时使用明确的 remote 和 branch 建立 upstream。

## 失败处理

- 无可提交变更：报告当前状态，不创建空 commit。
- hook 失败：保留完整错误，修复原因后重试；不使用 `--no-verify`。
- push 冲突：报告远端差异，先判断应 fetch/rebase 还是停止，不强推。
- 无法区分用户改动与任务改动：停止暂存并说明具体重叠文件。

## 输出

```text
Commit: <hash / 未执行>
Message: <title>
Files: <staged files>
Sign-off: yes / not executed
Push: <remote/branch / 未执行>
Verification: <actual checks>
```
