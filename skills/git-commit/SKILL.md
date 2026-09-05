---
name: git-commit
description: 用户明确要求生成提交信息、提交代码或提交后推送时使用；推送需明确授权。
compatibility: 需要 git。推送需要网络访问和已认证的远端。
allowed-tools: Bash(git add:*) Bash(git branch:*) Bash(git commit:*) Bash(git diff:*) Bash(git log:*) Bash(git status:*) Bash(git push:*)
---

# 创建规范化提交

## 边界

- 用户只要提交信息：输出草案，不暂存、不提交、不推送。
- 用户要求提交：检查并精准暂存目标文件，执行提交，不默认推送。
- 只有用户明确要求推送时才推送。
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

2. 根据用户授权和差异确定提交范围；混有无关改动时只暂存目标路径。
3. 根据仓库近期惯例生成 `<type>(<scope>): <summary>`：
   - `feat`、`fix`、`docs`、`refactor`、`perf`、`test`、`build`、`ci`、`chore`
   - 摘要使用祈使语气、现在时，不加句号或表情符号
   - 正文解释为什么改和影响范围；简单文档提交可省略
   - 按需加入 `BREAKING CHANGE:`、`DEPRECATED:`、`Fixes #123` 或 `Closes #123`
4. 暂存后再次检查：

   ```bash
   git diff --cached --stat
   git diff --cached
   ```

5. 执行 `git commit -s`。`-s` 是必需的签署声明，不得省略或用配置猜测替代。
6. 读取新提交的哈希和摘要。用户同时明确要求推送时，再推送当前分支；无上游分支时使用明确的远端和分支建立上游分支。

## 失败处理

- 无可提交变更：报告当前状态，不创建空提交。
- 钩子失败：保留完整错误，修复原因后重试；不使用 `--no-verify`。
- 推送冲突：报告远端差异，先判断应获取更新或变基还是停止，不强推。
- 无法区分用户改动与任务改动：停止暂存并说明具体重叠文件。

## 输出

```text
提交：<提交哈希 / 未执行>
提交信息：<标题>
文件：<已暂存文件>
签署声明：已添加 / 未执行
推送：<remote/branch / 未执行>
验证：<实际检查>
```
