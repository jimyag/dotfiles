---
name: update-pr-title-and-body
description: 在用户要求修改 PR 标题、PR body、补全模板、或让 reviewer 更容易理解当前 PR 时使用。适用于已有 PR 或待发 PR 分支的场景。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards plus GitHub CLI and network access.
when_to_use: PR 已存在或当前分支已经准备好发 PR，需要补全模板、改标题、改 body、补验证信息，或让 reviewer 更容易理解改动。
disable-model-invocation: true
---

# 更新 PR 标题和描述

开始时声明："我正在使用 update-pr-title-and-body skill 梳理并更新 PR 标题与描述。"

## 目标

基于 commit、diff、变更文件和验证信息，生成更容易让 reviewer 理解的 PR 标题与 body。

重点不是“润色文案”，而是准确表达：

- 这个 PR 解决了什么问题
- 主要改了哪些内容
- 哪些文件或行为最值得优先审阅
- 如何验证
- 风险点或注意事项

## 何时使用

- 用户说“改下 PR 标题/描述”
- 用户说“让这个 PR 更容易理解/更容易 review”
- 用户要求“按 PR 模板补全内容”
- 当前 PR 标题/body 过于模糊、过期、缺测试说明、缺上下文

## 何时不要使用

- 用户只是要创建 commit，不涉及 PR
- PR 尚未形成有效 diff，几乎没有可分析内容
- 需要先修 bug、补测试、拆 PR，而不是先改文案

## 输入来源

必须优先从以下信息生成内容，而不是凭空总结：

1. 当前分支名
2. 基线分支与 PR diff
3. 最近相关 commit
4. 变更文件与改动统计
5. 已执行的测试/验证信息
6. 仓库中的 PR 模板
7. 已有关联 issue、ticket、设计文档

## 必查信息

```bash
git branch --show-current
gh pr view --json number,title,body,url,baseRefName,headRefName
BASE_BRANCH="$(gh pr view --json baseRefName --jq '.baseRefName')"
git fetch origin
git log "origin/$BASE_BRANCH"..HEAD --oneline --no-decorate
git diff "origin/$BASE_BRANCH"...HEAD --stat
```

标题、body、语言、模板和 reviewer 关注点统一遵循 [PR 文案规则](../_shared/pr-content.md)。

## 执行流程

1. 识别当前 PR，并读取实际 `baseRefName`；若不存在 PR，则基于当前分支生成可用 title/body 草案，并明确说明 base branch 需要单独确认。
2. 收集 commit、diff、变更文件、测试信息。
3. 判断 PR 文案语言。
4. 检查是否存在 PR 模板。
5. 生成更清晰的标题候选。
6. 生成 body 草案：
   - 有模板按模板填充
   - 无模板按默认结构输出
7. 若用户要求直接修改远端 PR，则使用 `gh pr edit` 更新 title/body。
8. 输出最终标题、body 摘要，以及是否已更新远端 PR。

## 关键约束

- 不要伪造测试结果；未知就明确写未验证
- 不要把无关改动包装成“顺手优化”
- 不要隐藏 breaking change、迁移步骤、配置变更
- PR 模板存在时，不能跳过模板字段
- 默认优先提升可理解性，而不是追求辞藻

## 输出模板

```text
PR: #<number> <url 或 "未创建">
标题: <最终标题>
正文: 已生成/已更新
模板: 有/无
已更新: 是/否
备注: <需要 reviewer 重点关注的 1-2 点>
```
