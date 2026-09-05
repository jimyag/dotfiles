---
name: gh-stack
description: 使用 gh-stack GitHub CLI 扩展管理堆叠分支和拉取请求。适用于创建、推送、变基、同步、切换、查看、重组或合并相互依赖的 PR 链及堆叠差异。
compatibility: 需要 git、已认证的 GitHub CLI、网络访问和 github/gh-stack 扩展。
metadata:
  author: github
  version: "0.0.9"
---

# 管理堆叠拉取请求

使用 `gh stack` 管理线性分支链，每个分支对应一个聚焦的 PR，并以下一层分支为基准。

```text
main -> data-models -> api -> frontend
```

基础改动放在栈的下层，依赖它的使用方放在上层。无关工作使用独立的栈。

## 前置检查

```bash
git rev-parse --git-dir
git status --short
gh --version
gh auth status
gh extension list | rg 'github/gh-stack'
```

获得明确授权后安装：

```bash
gh extension install github/gh-stack
```

存在多个远端时，配置目标默认远端，或在支持的命令中传入 `--remote`：

```bash
git config remote.pushDefault origin
```

## 非交互规则

- 调用 `init`、`add` 和基于分支的 `checkout` 时始终传入分支名；省略参数可能触发交互提示。
- 始终使用 `gh stack submit --auto`；只有已准备好评审的 PR 才添加 `--open`。
- 始终使用 `gh stack view --json`；默认查看模式是交互式的。
- 使用常规 `git add` 和 `git commit`，明确控制每一层的改动。
- 修改较低层前先切换过去并在该层提交，然后运行 `gh stack rebase --upstack`。
- 分支由多个栈共享时，需要先检出一个无歧义的分支。
- 执行 `checkout <pr-number>` 前，必要时用 `gh stack unstack --local` 移除冲突的本地跟踪信息。
- 使用 `gh stack merge --yes` 合并；不要用 `gh pr merge` 替代堆叠 PR 的合并操作。

## 常用流程

创建并提交一个栈：

```bash
gh stack init data-models
# 编辑，然后执行 git add 和 git commit
gh stack add api
# 编辑，然后执行 git add 和 git commit
gh stack add frontend
# 编辑，然后执行 git add 和 git commit
gh stack submit --auto
gh stack view --json
```

修改较低层并更新依赖层：

```bash
gh stack checkout api
# 编辑，然后执行 git add 和 git commit
gh stack rebase --upstack
gh stack push
gh stack view --json
```

日常同步：

```bash
gh stack sync
gh stack view --json
```

执行相关操作前，阅读 [完整命令参考](references/complete-reference.md)，确认准确参数、栈链接、结构调整、冲突恢复、合并队列、退出码和各命令的具体行为。

## 恢复边界

- 变基冲突：解决报告的文件并暂存，然后执行 `gh stack rebase --continue`；无法安全解决时用 `gh stack rebase --abort` 中止。
- 多栈歧义：检出一个明确且不共享的分支，不要猜测。
- GitHub API 失败：重试前检查认证和标准错误输出。
- 栈状态被锁定：重试前确认没有正在运行的 `gh stack` 进程。
- 仓库不支持堆叠 PR：报告限制，不要用无关命令模拟。

## 验证

每次执行会修改状态的流程后，运行 `gh stack view --json`，验证分支顺序、基准分支、PR 状态和变基状态。报告实际命令及输出覆盖的范围，不要仅凭推送成功就宣称整个栈状态正常。
