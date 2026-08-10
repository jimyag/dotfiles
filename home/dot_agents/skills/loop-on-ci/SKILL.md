---
name: loop-on-ci
description: 在已有 PR 需要持续观察 CI、修复失败项并跟到全部检查变绿时使用。适用于不是一次性分析，而是要围绕同一个 PR 反复查看 checks、修复、推送、再验证的场景。
compatibility: Local Claude/Codex profile; requires client support for manual-invocation guards plus git, GitHub CLI, and network access.
when_to_use: 已经有 PR，需要围绕同一个 PR 反复看 checks、修失败项、推新提交、再验证，直到全绿或明确发现阻塞。
disable-model-invocation: true
---

# 持续跟进 CI

## 目标

围绕当前 PR 的 checks 持续修复问题，直到 CI 变绿或明确发现阻塞点。

## 核心原则

- 以 `gh pr checks` 作为 PR 检查状态的事实来源
- 一次尽量只修一个失败原因
- 每次 push 后都重新看 checks

## 基本流程

1. 先定位当前分支对应的 PR
2. 查看当前 checks 状态
3. 若已有失败项，先分析失败原因
4. 修复后 push
5. 重新查看 checks
6. 重复以上步骤直到全部通过或确认阻塞

## 常用命令

```bash
gh pr view --json number,url,headRefName
gh pr checks --json name,bucket,state,workflow,link
gh pr checks --watch --fail-fast
gh run view <run-id> --log-failed
```

## 何时不要使用

- 只是想分析一次 CI 失败，不需要持续跟进
- 当前还没有 PR

## 输出要求

- 当前 PR 是哪个
- 哪些检查失败
- 已做了哪些修复
- 当前是否已全绿
- 若未全绿，阻塞点是什么
