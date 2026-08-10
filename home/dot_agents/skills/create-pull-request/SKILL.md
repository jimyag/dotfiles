---
name: create-pull-request
description: 在用户要求创建 PR、发起 review、或把当前分支提交给别人审阅时使用。适用于已有提交且准备正式发起 Pull Request 的场景。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards plus git, GitHub CLI, and network access.
when_to_use: 当前分支已有提交、工作区干净，用户明确要创建 PR、发起 review 或把当前分支提交给别人审阅；不是只改 PR 文案。
disable-model-invocation: true
---

# 创建 Pull Request

开始时声明："我正在使用 create-pull-request skill 创建规范化 PR。"

## 目标

基于当前分支的 commit、diff、验证信息和仓库 PR 模板，创建一个清晰、可审阅的 GitHub PR。

## 职责边界

- 本 skill 只负责创建 PR。
- 如果用户要改 commit message，使用 `git-commit`。
- 如果用户要修改已存在 PR 的标题或 body，使用 `update-pr-title-and-body`。

## 何时使用

- 用户说“创建 PR”
- 用户说“帮我提一个 pull request”
- 用户说“把当前分支发起 review”

## 何时不要使用

- 工作区还有未提交变更
- 当前分支已经有 PR，且用户只是要改标题或 body
- 用户只是要提交 commit，不需要创建 PR

## 预检查

```bash
gh --version
gh auth status
git status --short
git branch --show-current
gh pr list --head "$(git branch --show-current)" --json number,title,url,state
```

规则：

- `gh` 未安装或未登录时停止，并明确报错。
- 工作区不干净时停止，先让用户提交或清理变更。
- 当前分支已存在 PR 时，不重复创建；引导改用 `update-pr-title-and-body` 或直接查看现有 PR。

## base branch 规则

不要写死 `main`。

创建 PR 时，base branch 按以下顺序确定：

1. 若存在 `upstream` remote，则取 `upstream` 仓库的 default branch
2. 否则取 `origin` 仓库的 default branch

示例命令：

```bash
if git remote get-url upstream >/dev/null 2>&1; then
  BASE_REMOTE="upstream"
else
  BASE_REMOTE="origin"
fi

BASE_BRANCH="$(gh repo view --repo \"$(git remote get-url \"$BASE_REMOTE\")\" --json defaultBranchRef --jq '.defaultBranchRef.name')"
git fetch "$BASE_REMOTE"
git log "$BASE_REMOTE/$BASE_BRANCH"..HEAD --oneline --no-decorate
git diff "$BASE_REMOTE/$BASE_BRANCH"...HEAD --stat
```

## PR 模板

标题、body、语言和模板处理统一遵循 [PR 文案规则](../_shared/pr-content.md)。

## 创建流程

1. 检查 `gh`、认证、工作区、当前分支、现有 PR。
2. 识别 base remote 与其 default branch。
3. 基于 `BASE_REMOTE/BASE_BRANCH` 收集 commit 和 diff。
4. 判断 PR 文案语言。
5. 检查 PR 模板。
6. 生成标题和 body：
   - 有模板时按模板填充
   - 无模板时至少包含摘要、关键改动、验证、备注
7. 推送当前分支：
   - 已有上游时 `git push`
   - 无上游时 `git push -u origin <current-branch>`
8. 创建 PR：
   - 普通 PR：`gh pr create --base "$BASE_BRANCH" --title "$PR_TITLE" --body "$PR_BODY"`
   - Draft PR：仅在用户明确要求或改动尚未准备好 review 时使用 `--draft`

## 输出模板

```text
PR: #<number> <url>
Base: <base-remote>/<base-branch>
标题: <最终标题>
模板: 有/无
草稿: 是/否
推送: 成功/失败
```

## 失败回退

- 已存在 PR：输出 PR 编号和链接，不重复创建
- 无法识别 default branch：输出 remote 信息并停止
- push 失败：输出报错，不创建 PR
- 模板存在但无法正确填充：停止并说明缺失信息
