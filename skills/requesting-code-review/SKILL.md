---
name: requesting-code-review
description: 在功能完成、准备提 PR 或合并，或需要系统审查当前 diff/PR 时使用。基于完整变更和真实代码检查正确性、回归、复杂度、性能、安全、文档、语言专项与架构风险；默认只读，不用于处理别人已给出的 review 意见。
compatibility: Local diff review requires git. GitHub PR retrieval or review publication requires an available GitHub connector or authenticated gh CLI.
---

# 系统性 Code Review

## 边界

- 审查当前本地 diff 或指定 GitHub PR，默认只分析和报告。
- `receiving-code-review` 处理别人已经给出的意见。
- 不修改文件、不提交、不 push；只有用户明确要求发布 review 时才执行远端写入。
- 不要求特定客户端插件。GitHub connector 可用时优先使用，否则回退 `gh`；两者都不可用时仍可审查本地 diff，远端操作明确报告未执行。

## 1. 固定审查快照

先确认仓库、工作区和审查范围：

```bash
git rev-parse --git-dir
git status --short
git branch --show-current
git log --oneline -10
```

PR 模式通过当前可用的 GitHub 能力读取 number、base/head、state、updated time、完整 diff 和 checks。本地模式读取 `git diff HEAD` 或明确的 `<base>...HEAD`。记录实际 range，不基于旧 diff 或截断 hunk 下结论。

完整 diff、逐文件覆盖、可信上下文、行号定位和反证规则遵循 [Review 证据协议](references/evidence-protocol.md)。标准或深入审查先执行 [范围与完整性预判](references/review-preflight.md)。

## 2. 确定深度与专项

- 快速：100 行以内且 1-5 个文件
- 标准：100-500 行，或 6-10 个文件
- 深入：500 行以上、10 个以上文件，或涉及认证、支付、数据写入等高风险路径

只根据本轮变更加载专项：

- 通用正确性、边界、错误处理、测试与复杂度：[代码质量](references/code-quality.md)
- 明确热点、I/O/网络放大、锁或分配风险：[性能](references/performance.md)
- 信任边界、鉴权、输入或密钥风险：[安全](references/security.md)
- 行为、API、配置或示例变化：[文档](references/documentation.md)
- `.go` / `go.mod`：[Go](references/go-specialist.md)
- `.java`：[Java](references/java.md)
- `.py`：[Python](references/python.md)
- CI、YAML/JSON 配置或依赖 manifest：[CI/config](references/ci-config.md)

TS/JS 变更执行轻量语言检查，不因仓库存在某语言就加载无关清单。

## 3. 架构分路

用户明确要求架构评审，或 diff 改变模块分层、公共接口、adapter/middleware、状态或任务生命周期、存储、跨服务调用、权限、错误体系、并发与资源管理时，加载 [架构审查](references/architecture.md)。

架构结论必须基于当前 diff 和必要相邻实现。区分必须修复与可选优化，不把理想化分层、个人偏好或未触及历史问题包装成缺陷。

## 4. 证据过滤与汇总

对每个候选 finding：

1. 读取定义、调用方、配置和测试等必要上下文；hunk 不足时查真实代码。
2. 找能推翻关键事实的反证，有直接反证就删除。
3. 确认问题由当前变更引入或暴露，并定位到当前快照最小连续范围。
4. 内部评估置信度：`80+` 才作为问题；`50-79` 放入待确认；低于 50 不输出。
5. 按文件和根因去重，再按 P0/P1/P2 排序。

严重度：

- P0：确定的正确性、安全或严重并发缺陷
- P1：健壮性、关键测试缺口或明确性能退化
- P2：有实际维护成本的设计、文档或规范问题

不为凑数量报告问题。默认检查是否存在可删除的抽象、依赖和配置层，但安全校验、错误处理、数据保护、可访问性和用户明确需求不算无效复杂度。

## 5. 发布 review

只有用户明确要求把结果发布到 GitHub 时：

1. 完成所有适用检查和去重后再发布，避免中途制造多次通知。
2. 使用当前可用的 connector；不支持写入时回退 `gh api`。
3. 只发布一次 non-blocking `COMMENT`，不擅自使用 `REQUEST_CHANGES`。
4. 发布后读回 review，验证目标 PR、正文和事件类型。
5. 没有远端写能力时输出完整 review body 和人工执行说明，不声称已经发布。

## 输出

```text
## 问题
[P0/P1/P2] <标题> - <文件:行> [置信度: 90]
证据: <触发条件、当前代码和影响>
建议: <最小可执行修复>

## 待确认问题
- <缺少的关键证据>

## 摘要
- diff 快照：<range>
- 文件覆盖：<已审查 / 上下文 / 跳过 / 失败>
- 范围与需求：<结论>
- 可拆分性与文档债务：<结论>
- 架构专项：<未执行或基于证据的结论>
- 发布：<未请求 / connector / gh / 未执行>
```

问题最多 15 条。没有高置信问题时明确写“未发现明确问题”，并说明验证和上下文边界。
