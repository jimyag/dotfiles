---
name: loop-on-ci
description: 在已有 GitHub PR 需要持续观察 Actions checks、读取失败 job 日志、修复问题、重新运行并跟到全部检查变绿时使用。适用于围绕同一个 PR 反复验证，而不是一次性状态查询。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards, git, a GitHub connector with Actions run/job/log access, and network access.
when_to_use: 已经有 GitHub PR，需要围绕同一个 head 反复读取 Actions 状态和日志、修复失败项、推送、重跑并验证，直到全绿或明确发现阻塞。
disable-model-invocation: true
---

# 持续跟进 GitHub Actions

## 目标

围绕当前 PR 的 GitHub Actions checks 持续修复问题，直到全部通过或确认阻塞点。GitHub connector 是 PR、workflow、job、step 和日志状态的事实来源。

## 核心原则

- 每轮先确认 PR head SHA，避免分析旧 run 或旧日志。
- 通过 connector 按 `PR -> head SHA -> workflow runs -> jobs -> steps/logs` 获取证据。
- 一次只处理一个明确失败原因；每次 push 后重新读取 PR head 与新 runs。
- 不用 `gh` CLI 复制 connector 已提供的 Actions 能力。
- `codecov/project`、`codecov/patch`、flag 或 component 失败转给 `codecov-coverage`。

## 基本流程

1. 确认目标 repo、PR、当前分支、工作区和 PR head SHA。
2. 用 GitHub connector 获取该 commit 对应的 pull-request workflow runs。
3. 对失败 run 获取 jobs，再读取失败 job 的 steps 和完整日志。
4. 用日志与代码/配置建立根因证据链；证据不足时报告缺失项，不猜测 flaky。
5. 修复当前 PR 引入的问题，运行仓库允许且与改动对应的验证。
6. 提交并推送后确认 PR head 已更新，再等待并读取新 run；不要复用旧 run 的结论。
7. 需要重跑时优先使用 connector 重跑单个 job；只有多个失败 job 共享同一原因时才重跑全部失败 jobs。
8. 重复直到全部 GitHub Actions checks 通过，或遇到权限、外部依赖、无日志、head 并发更新等明确阻塞。

## Connector 边界

- 当前 connector 只返回 pull-request-triggered runs 和第一页结果。目标 run/job 不在结果中时，报告分页或触发类型限制，不声称 CI 不存在。
- connector 缺少 Actions read/write 权限时，明确缺失权限；不自动切换到其他凭据或执行写操作。
- 非 GitHub Actions check 不伪装成 Actions job。Codecov 使用 `codecov-coverage`；其他外部 CI 只报告名称和链接，除非用户另行指定处理方式。

## 何时不要使用

- 只是读取一次 PR 或 workflow 状态，不需要持续跟进。
- 当前还没有 PR。
- 只是 Codecov 覆盖率查询或 gate 失败，使用 `codecov-coverage`。
- 本地测试或普通代码异常，使用 `systematic-debugging`。

## 输出要求

- PR、当前 head SHA 和本轮 workflow run。
- 每个失败 job 的关键日志证据与代码/配置路径。
- 已做的修复、验证、commit/push 和 rerun 状态。
- 当前是否全部通过；未通过时给出准确阻塞点。
