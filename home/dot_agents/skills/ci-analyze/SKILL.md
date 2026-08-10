---
name: ci-analyze
description: 在用户提到 CI 失败、pipeline 失败、构建失败、测试失败，或需要定位 PR 检查为何变红时使用。适用于需要基于日志和代码证据判断失败根因的场景。
allowed-tools: >-
  Read Grep Glob Bash(gh run list:*) Bash(gh run view:*) Bash(gh pr view:*)
  Bash(gh pr checks:*) Bash(gh api *) Bash(git *) Bash(curl *) Bash(jq *)
  Bash(cat *) Bash(wc *) Bash(head *) Bash(tail *) Bash(grep *)
---

# CI 失败分析

开始时声明："我正在使用 ci-analyze skill 分析 CI 失败原因。"

## 核心原则

1. 枚举并分析全部失败，不只看第一个。
2. 为每项建立日志到代码或配置的证据链。
3. 给出已确认根因，或明确标记缺失证据；同时给出下一步修复或验证动作。

## 证据链硬约束

每个失败项至少要给出下面两类证据，缺一不可：

1. 日志证据：
   - 至少 1 行关键报错
   - 说明这行报错为什么能代表失败根因，而不只是表面现象
2. 代码或配置证据：
   - 至少 1 个对应的代码路径、配置路径或脚本路径
   - 说明错误是如何从这里传播到 CI 失败的

缺少任一类证据时标记为“待补证据”，不得下高置信度结论或判定为 flaky。

## 执行流程

### 步骤 1：获取失败列表

```bash
# 获取 PR 的 CI checks
gh pr checks <PR编号> --repo <owner/repo>

# 或获取最近一次 workflow run 的失败
gh run list --repo <owner/repo> --branch <branch> --limit 5
gh run view <run-id> --repo <owner/repo> --log-failed
```

如果是 PR，先把外部 CI（Travis/Codecov）入口抓出来，避免漏查：

```bash
gh pr view <PR编号> --repo <owner/repo> \
  --json statusCheckRollup \
  --jq '.statusCheckRollup[]? | {name: .context, state: .state, url: .targetUrl}'
```

### 步骤 1.5：按 CI 提供方抓取日志

根据失败的 check 类型（GitHub Actions / Travis CI / Codecov），使用对应方式抓取完整日志。

各提供方的详细命令与认证方式参见 `references/ci-log-fetching.md`。

关键要点：
- GitHub Actions：`gh run view <run-id> --log-failed`
- Travis CI：使用 TRAVIS_TOKEN 认证，命令禁止管道组合，输出先存 /tmp
- Codecov：从 commit check-runs API 获取，补充 project/patch 状态

### 步骤 2：分析每个失败

对每个失败的 check/job：

1. 获取完整错误日志
2. 定位失败的测试或步骤
3. 在代码中找到对应位置
4. 检查 git blame 看最近改动
5. 判断根因类别：
   - regression：我们的代码改动导致
   - flaky：间歇性基础设施问题（需要证据：同一测试在 3+ 次其他运行中通过）
   - environment：配置或依赖问题
6. 为每个失败建立证据链：
   - 关键报错日志行
   - 对应代码/配置/脚本路径
   - 错误传播路径或触发条件

### 步骤 3：输出分析报告

- 失败汇总表：最多列出 20 条，超出用「其余见日志」概括。
- 详细分析：每项「根因分析 + 修复建议」合计不超过 300 字；只保留值得写的项。
- 禁止输出敏感信息：禁止在报告、总结或日志回显中包含完整 token（如 TRAVIS_TOKEN）；仅可写「已使用 Travis API 认证」等抽象描述。

```plaintext
## CI 失败分析报告

### 失败汇总

| 序号 | 测试/Job | 错误类型 | 根因 | 置信度 |
|------|----------|----------|------|--------|
| 1    | ...      | ...      | ...  | 高/中/低 |

### 详细分析

#### 失败 1: <测试名>

错误信息：
<具体错误日志>

日志来源：
<GitHub Actions/Travis/Codecov + URL 或 API 端点>

根因分析：
<分析过程>

修复建议：
<具体修复方案>

相关代码：
<文件路径:行号>
```

### 步骤 4：提出修复方案

- 对于 regression 类型：给出具体代码修复
- 对于 flaky 类型：说明判断依据，建议重跑或标记 flaky
- 对于 environment 类型：说明配置修复方案

## 判断 flaky 的证据要求

只有满足以下条件才能判定为 flaky：

1. 同一测试在同一分支的最近 3+ 次运行中至少有 1 次通过
2. 错误信息显示明确的基础设施问题（网络超时、资源不足等）
3. 代码路径没有最近改动

```bash
# 检查历史运行
gh run list --repo <owner/repo> --branch <branch> --workflow <workflow> --limit 10
```

对于 Travis/Codecov 也要补历史证据（同一 job/check 在最近多次提交中的结果），不能只看单次失败。

## 日志收集超时与降级策略

1. 单个系统（GHA/Travis/Codecov）日志抓取超过 5 分钟，立即进入降级：
   - 先用已有摘要继续根因判断
   - 明确标注"证据等级下降"的原因（权限/接口失败/日志截断）
2. 禁止输出敏感信息：若 token 疑似泄露（例如出现在聊天记录或终端共享），立即提醒用户撤销并重新生成；日志与报告中不得回显 token 明文，仅可写「已使用 xxx 认证」。
3. 最终报告必须区分：
   - 已确认根因（高置信度）
   - 待补日志验证项（中/低置信度）

## 失败回退

- 日志抓取失败（权限/接口异常）：记录失败命令与关键报错，按降级策略使用已有摘要继续分析，并在结论中标注证据等级下降。
- 外部凭证缺失（如 `TRAVIS_TOKEN`）：输出缺失项、已尝试步骤和配置指引，停止对应日志抓取步骤，不阻塞其他已可分析的失败项。
- 无法确定根因：将该项标记为“待补日志验证”，列出缺失证据和下一步需要的输入。

## 统一约束

- 验收标准：遵循 `skills/_shared/common-acceptance.md`
- 系统规范：遵循 `home/dot_agents/AGENTS.md`
- 本 skill 的额外约束：只有满足“判断 flaky 的证据要求”时才能归因为 flaky。
