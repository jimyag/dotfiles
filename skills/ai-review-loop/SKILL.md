---
name: ai-review-loop
description: 仅当用户明确点名 `ai-review-loop` 或输入 `/ai-review-loop`，要求推进 GitHub PR 的远程 AI 评审闭环时使用；不得根据普通评审、PR、CI 或修复请求自动触发。
compatibility: 本地 Claude/Codex 配置；需要客户端支持手动调用限制、工具禁用、参数提示和 GitHub CLI 访问。
when_to_use: 用户手动调用后，先识别当前来源分支版本已有的机器人评审和仓库可用的 FennoAI、Codex、Claude 或 Gemini 集成，再选择对应入口触发评审并处理成立问题。
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

# AI 评审闭环

手动推进 GitHub PR 的远程 AI 评审者闭环。调用本技能视为授权在目标 PR 范围内处理成立问题、验证、提交并推送；不授权强制推送、扩大改动范围或处理其他 PR。

## 评审者识别与触发

- 不申请组织管理权限，也不查询 GitHub App 安装列表。从当前 PR 或最多最近 20 个 PR 的机器人或应用评论、评审、表态、检查或工作流识别集成；没有记录只表示“未确认”，不等于未安装。
- FennoAI：优先发送 `/review -claude`；命令失败或不受支持时回退一次 `/review`。
- Codex App：发送 `@codex review`。
- Claude App：发送 `@claude review this pull request`。
- Gemini Code Assist：发送 `/gemini review`。
- 同时存在多个集成时，优先 FennoAI，再处理其他集成；只触发当前来源分支版本尚无结果且未在运行的评审者。
- 没有识别到任何集成时，按上述顺序逐个做一次有界探测；前一个入口无响应并清理探测评论后才能尝试下一个，任一入口确认可用后停止探测。
- `max-rounds` 默认 5，只计算本次调用中新触发的评审；单个评审者等待完成不超过 10 分钟，整次调用不超过 30 分钟。
- `change-notes` 与评审者意见一起按代码证据判断，不能覆盖项目约定。

## 探测确认与评论清理

- 发出触发评论后记录 `{reviewer, triggerNodeId, baselineSHA, triggerAt}`，并在 2 分钟内每 30 秒轮询。表态必须来自目标评审者且作用于该触发评论；评论、评审、检查或工作流必须来自目标评审者，晚于 `triggerAt` 且绑定 `baselineSHA`，才算已确认。
- 有确认或仍在运行时保留触发评论。2 分钟内完全无确认时，将该评审者标记为“未确认”，只把本次调用创建的触发评论最小化为 `OUTDATED`，不得删除或隐藏其他人的评论。
- 最小化需要仓库写入权限；调用 `gh api` 前单独请求授权，API 写入只允许对已记录的 `triggerNodeId` 执行 `minimizeComment(OUTDATED)`。权限不足时保留评论并在汇报中说明，不因此重试触发命令。

## 每轮流程

1. 读取 PR 元数据、当前来源分支提交 SHA、评审、问题评论、行内评论、表态和检查；记录本地 HEAD、分支、上游分支与工作区状态。
2. 从当前和近期 PR 的机器人活动识别可用集成，并检查当前来源分支版本已有的结果：
   - 已有可执行评论：先判断和处理，不再重复触发对应评审者。
   - 已有完成且无可执行评论的评审：记录为已通过，不重复触发。
   - 与当前评审者、`triggerNodeId` 和来源分支提交 SHA 全部匹配的 `eyes` 表态：视为处理中，只轮询。
   - 属于旧来源分支版本的评论、触发记录和表态：保留为历史，不阻止当前来源分支版本重新评审。
3. 按“评审者识别与触发”的映射发送一次触发命令；未知集成遵循“探测确认与评论清理”，不能并行撒出所有命令。
4. 按评论时间、来源分支提交 SHA、位置和评审者身份筛出新反馈，标记为 `成立`、`过期`、`超出范围` 或 `需澄清`。
5. 只修复由当前 PR 引入且有代码证据的问题；存在歧义、范围扩张或相互冲突的评审者意见时停止并请求用户判断。
6. 使用仓库规定的定向检查验证改动，分别记录本地验证和远程检查。验证命令未预授权时先请求授权；未获授权或验证失败时不得提交。
7. 提交前复核差异和暂存范围，确认远程来源分支版本仍等于本轮基准 SHA，且上游分支对应 PR 来源分支版本。
8. 使用 `git-commit` 创建带签署声明的提交并推送；用户显式调用 `ai-review-loop` 已满足该提交的确认要求，不再逐轮停下等待。
9. 推送后确认远程来源分支版本更新，等待 5 秒，再从“已有机器人结果”检查开始下一轮。

## 评审者失败

- FennoAI 的 `/review -claude` 失败时回退一次 `/review`；其他评审者仅重试原命令一次，仍失败则停止该评审者。
- “命令失败”必须有机器人错误回复或 workflow/check 失败证据；完全无响应属于未确认，不重试同一命令。
- 已确认的评审者每 30 秒轮询，单次触发最多等待 10 分钟；到期仍没有新反馈时报告待处理并停止该评审者。整次调用达到 30 分钟时立即汇报当前状态，不无限等待。
- 无法获得讨论已解决状态时，按评论的提交、位置和过期状态判断，并披露限制。

## 停止条件

- 已识别的评审者在当前来源分支版本上都没有可执行反馈。
- PR 来源分支版本被其他人更新，或本地存在会混入提交的无关改动。
- 评论含义不清、评审者结论冲突或修复会扩大 PR 范围。
- CI 出现与本轮无关且阻塞继续判断的失败。
- 达到 `max-rounds`。

## 汇报

每轮记录评审者、基准和最新来源分支提交 SHA、复用的已有机器人结果、新触发命令、接受或拒绝的评论及理由、修改文件、验证结果、提交和推送状态和剩余检查。只有重新读取最新 PR 状态后，才能说“没有剩余可执行评审意见”。
