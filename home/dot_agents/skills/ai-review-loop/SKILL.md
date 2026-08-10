---
name: ai-review-loop
description: 仅当用户明确点名 `ai-review-loop` 或输入 `/ai-review-loop`，要求推进 GitHub PR 的远程 AI review 闭环时使用；不得根据普通 review、PR、CI 或修复请求自动触发。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards, denied tools, argument hints, and GitHub CLI access.
when_to_use: 用户手动调用后，先识别当前 head 已有的机器人 review 和仓库可用的 FennoAI、Codex、Claude 或 Gemini 集成，再选择对应入口触发 review 并处理成立问题。
disable-model-invocation: true
argument-hint: "<PR URL | PR编号> [max-rounds=5] [change-notes=<修改意见>]"
allowed-tools: >-
  Bash(git status:*) Bash(git branch:*) Bash(git rev-parse:*) Bash(git fetch:*)
  Bash(git switch:*) Bash(git diff:*) Bash(git add:*) Bash(gh pr view:*)
  Bash(gh pr checks:*) Bash(gh pr comment * --body *) Bash(sleep:*)
  Skill(git-commit)
disallowed-tools:
  - Bash(git push --force*)
  - Bash(git push * --force*)
  - Bash(git push * -f*)
  - Bash(gh pr comment * --body-file *)
  - Bash(gh pr comment * -F *)
  - Bash(gh pr comment * --delete-last*)
---

# AI Review Loop

手动推进 GitHub PR 的远程 AI reviewer 闭环。调用本 skill 视为授权在目标 PR 范围内处理成立问题、验证、提交并推送；不授权 force push、扩大改动范围或处理其他 PR。

## Reviewer 识别与触发

- 不申请组织管理权限，也不查询 GitHub App 安装列表。从当前 PR 或最多最近 20 个 PR 的 bot/app 评论、review、reaction、check 或 workflow 识别集成；没有记录只表示“未确认”，不等于未安装。
- FennoAI：优先发送 `/review -claude`；命令失败或不受支持时回退一次 `/review`。
- Codex App：发送 `@codex review`。
- Claude App：发送 `@claude review this pull request`。
- Gemini Code Assist：发送 `/gemini review`。
- 同时存在多个集成时，优先 FennoAI，再处理其他集成；只触发当前 head 尚无结果且未在运行的 reviewer。
- 没有识别到任何集成时，按上述顺序逐个做一次有界探测；前一个入口无响应并清理探测评论后才能尝试下一个，任一入口确认可用后停止探测。
- `max-rounds` 默认 5，只计算本次调用中新触发的 review；单个 reviewer 等待完成不超过 10 分钟，整次调用不超过 30 分钟。
- `change-notes` 与 reviewer 意见一起按代码证据判断，不能覆盖项目约定。

## 探测确认与评论清理

- 发出触发评论后记录 `{reviewer, triggerNodeId, baselineSHA, triggerAt}`，并在 2 分钟内每 30 秒轮询。reaction 必须来自目标 reviewer 且作用于该 trigger comment；评论、review、check 或 workflow 必须来自目标 reviewer，晚于 `triggerAt` 且绑定 `baselineSHA`，才算已确认。
- 有确认或仍在运行时保留触发评论。2 分钟内完全无确认时，将该 reviewer 标记为“未确认”，只把本次调用创建的触发评论最小化为 `OUTDATED`，不得删除或隐藏其他人的评论。
- 最小化需要仓库 write 权限；调用 `gh api` 前单独请求授权，API 写入只允许对已记录的 `triggerNodeId` 执行 `minimizeComment(OUTDATED)`。权限不足时保留评论并在汇报中说明，不因此重试触发命令。

## 每轮流程

1. 读取 PR metadata、当前 head SHA、reviews、issue comments、inline comments、reactions 和 checks；记录本地 HEAD、分支、upstream 与工作区状态。
2. 从当前和近期 PR 的机器人活动识别可用集成，并检查当前 head 已有的结果：
   - 已有 actionable comments：先判断和处理，不再重复触发对应 reviewer。
   - 已有完成且无 actionable comments 的 review：记录为已通过，不重复触发。
   - 与当前 reviewer、`triggerNodeId` 和 head SHA 全部匹配的 `eyes` reaction：视为处理中，只轮询。
   - 属于旧 head 的评论、触发记录和 reaction：保留为历史，不阻止当前 head 重新 review。
3. 按“Reviewer 识别与触发”的映射发送一次触发命令；未知集成遵循“探测确认与评论清理”，不能并行撒出所有命令。
4. 按评论时间、head SHA、位置和 reviewer 身份筛出新反馈，标记为 `成立`、`过期`、`超出范围` 或 `需澄清`。
5. 只修复由当前 PR 引入且有代码证据的问题；存在歧义、范围扩张或相互冲突的 reviewer 意见时停止并请求用户判断。
6. 使用仓库规定的 targeted checks 验证改动，分别记录本地验证和远程 checks。验证命令未预授权时先请求授权；未获授权或验证失败时不得 commit。
7. commit 前复核 diff 和 stage 范围，确认远程 head 仍等于本轮基准 SHA，且 upstream 对应 PR head。
8. 使用 `git-commit` 创建带 sign-off 的 commit 并 push；用户显式调用 `ai-review-loop` 已满足该 commit 的确认要求，不再逐轮停下等待。
9. push 后确认远程 head 更新，等待 5 秒，再从“已有机器人结果”检查开始下一轮。

## Reviewer 失败

- FennoAI 的 `/review -claude` 失败时回退一次 `/review`；其他 reviewer 仅重试原命令一次，仍失败则停止该 reviewer。
- “命令失败”必须有 bot 错误回复或 workflow/check 失败证据；完全无响应属于未确认，不重试同一命令。
- 已确认的 reviewer 每 30 秒轮询，单次触发最多等待 10 分钟；到期仍没有新反馈时报告 pending 并停止该 reviewer。整次调用达到 30 分钟时立即汇报当前状态，不无限等待。
- 无法获得 thread resolved 状态时，按 comment 的 commit、位置和 outdated 状态判断，并披露限制。

## 停止条件

- 已识别的 reviewer 在当前 head 上都没有可执行反馈。
- PR head 被其他人更新，或本地存在会混入提交的无关改动。
- 评论含义不清、reviewer 结论冲突或修复会扩大 PR 范围。
- CI 出现与本轮无关且阻塞继续判断的失败。
- 达到 `max-rounds`。

## 汇报

每轮记录 reviewer、基准和最新 head SHA、复用的已有机器人结果、新触发命令、接受或拒绝的评论及理由、修改文件、验证结果、commit/push 状态和剩余 checks。只有重新读取最新 PR 状态后，才能说“没有剩余可执行 review 意见”。
