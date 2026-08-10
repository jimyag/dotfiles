---
name: requesting-code-review
description: 在功能完成、准备提 PR、准备合并、或希望对当前 diff/PR 做系统性代码检查时使用。适用于需要先看风险、回归和审查重点的场景。
allowed-tools: >-
  Read Glob Grep Bash(rg:*) Bash(git diff:*) Bash(git log:*)
  Bash(git status:*) Bash(ls:*) Bash(gh pr view:*) Bash(gh pr diff:*)
  Bash(gh pr checks:*) Bash(gh api:*)
---

# 发起 Code Review

开始时声明："我正在使用 requesting-code-review skill，将按适用的审查分路分步执行后汇总。"

## 职责边界

- 本 skill 负责"主动检查当前改动"——本地自查或指定 PR 审查
- `receiving-code-review` 负责"处理别人已经给出的 review 意见"，两者不重叠
- 仅支持本地 diff 与 GitHub PR；不支持 GitLab/MR

## 复杂度分路（默认）

- 默认检查是否存在不必要的抽象、依赖或配置层；只有证据充分且能降低真实复杂度时报告，不作为默认阻塞项
- 按 YAGNI、现有实现、标准库、平台能力、已安装依赖的顺序检查，报告第一个足够的替代方案
- 用 `file:Lx: delete|stdlib|native|yagni|shrink: ...` 定位问题；只报告能减少真实复杂度且证据充分的项
- 不把安全校验、错误处理、数据保护、可访问性或用户明确要求的复杂度建议删除

## 何时使用

- 功能做完准备提 PR，先做一轮自查
- 改了核心逻辑，想确认没有带出新问题
- 修完 bug，想验证没有引入回归
- 合并前做最后一轮检查
- 明确提供了 PR 编号或 URL，做系统性 PR 审查

## 何时不要使用

- 只是要提交 commit 或创建 PR 文案
- 当前改动尚未形成有效 diff
- 收到了别人的 review 意见需要处理（用 `receiving-code-review`）
- 用户要求审查 GitLab MR

---

## Step 0：上下文检测

**模式判断：**

有 PR 编号或 URL → PR 模式：

```bash
git rev-parse --git-dir
git status --short
gh pr view <pr> --repo <owner/repo> --json number,headRefName,baseRefName,state,updatedAt
gh pr diff <pr> --repo <owner/repo>
gh pr checks <pr> --repo <owner/repo>
```

无 PR 信息 → 本地 diff 模式：

```bash
git rev-parse --git-dir
git status --short && git diff --stat && git diff HEAD
git log --oneline -10
# 或按 base branch 对比
git diff <base-branch>...HEAD
```

完整 diff、逐文件覆盖、可信上下文和 hunk 解读统一遵循 [Review 证据协议](references/evidence-protocol.md)。开始分路前必须记录实际 review range；仓库文档已有验证命令时沿用现有流程。

**审查深度：**

- 快速：100 行以内且 1-5 个文件
- 标准：100-500 行，或 6-10 个文件
- 深入：500+ 行、10+ 文件，或涉及认证、支付、数据写入等高风险改动

先标注深度，再进入分路审查。深入审查在代码质量分路中追加结构维护性检查，重点看复杂度增长、抽象边界、文件膨胀和架构漂移，但不要把可选重构包装成阻塞缺陷。

**架构专项触发：**

出现以下任一情况时，额外执行步骤 6：

- 用户明确要求架构评审、深度架构评审、抽象/分层/模块边界审查，或要求识别过度设计、空抽象、无效模块
- 本次 diff 新增或重组模块分层、接口、adapter、middleware、runtime、调度、状态管理、存储、跨服务调用或公共工具层
- 本次 diff 改动核心链路、跨层依赖、错误体系、权限边界、配置加载、会话/任务生命周期、并发控制或资源管理
- 深入审查中发现复杂度明显上升，例如新增多层转发、重复概念、薄 wrapper、隐式全局状态或职责不清的共享模块

架构专项仍遵守 diff 快照、置信度过滤和只读协议；不要把个人偏好、理想化分层或未触及的历史问题包装成当前 PR 缺陷。

**文件类型专项路由：**

```bash
# 只根据本轮变更文件选择专项规则，不因仓库里存在某种语言就加载无关清单
git diff --name-only <review-range>
```

- 变更包含 `.go` 或 `go.mod` → 步骤 5 加载 [references/go-specialist.md](references/go-specialist.md)。
- 变更包含 `.ts`、`.tsx`、`.js`、`.jsx`、`package.json` 或 `tsconfig.json` → 在代码质量分路执行 TS/JS 轻量检查。
- 变更包含 `.java` → 加载 [references/java.md](references/java.md)。
- 变更包含 `.py` → 加载 [references/python.md](references/python.md)。
- 变更包含 `.github/workflows/*.yml`、`.github/workflows/*.yaml`、通用 YAML/JSON 配置或依赖 manifest → 加载 [references/ci-config.md](references/ci-config.md)。
- 多种文件类型同时出现时可加载多个专项 reference，但每份规则只作用于匹配的变更文件；没有命中时不要读取，避免清单噪声。

**默认只读协议：**

只分析和报告，不修改文件、不提交、不 push、不发布评论。证据不足时写"需补充上下文"，不猜。

**置信度过滤：**

每条问题内部先做 0-100 置信度判断：

- `80+`：有当前 diff 和上下文证据，触发条件明确，值得报告
- `50-79`：可能成立但还缺一个关键证据，默认放入待确认问题
- `<50`：主观偏好、可能是既有问题或证据不足，不输出

默认只输出 `80+` 的问题。不要为了凑数量报告低置信建议。高影响但证据仍有限的问题可以输出，但必须显式写清不确定点和需要补充验证的条件。

**GitHub 发布协议（仅用户明确要求发布 review 时执行）：**

1. 先完成步骤 1-6 中适用的检查并去重，不要在中途发布评论
2. 只发布一次 non-blocking review，避免逐条评论制造多次通知
3. 通过 `gh api` 创建 review，event 只能使用 `COMMENT`，不能使用 `REQUEST_CHANGES`
4. review body 开头包含 `<!-- codeagent-review-id: pr-<number> -->`
5. 发布后在最终输出包含 `<!-- codeagent-execution-completed -->`

---

## Step 0.5：范围与完整性预判

按 [Review 范围与完整性预判](references/review-preflight.md) 检查目标一致性、需求合规、可拆分性、模式修复完整性、高风险缺口和反证。标准或深入审查必须分别形成需求轴与工程轴结论。

---

## 步骤 1：代码质量分路

检查要点见 [references/code-quality.md](references/code-quality.md)。

覆盖：命名、函数规模与职责、错误处理、边界条件、逻辑正确性、回归风险、测试覆盖、项目约定。深入审查追加结构维护性检查。

只记录值得处理的问题；无则记"代码质量：无明确问题"。

---

## 步骤 2：性能分路

检查要点见 [references/performance.md](references/performance.md)。

覆盖：重复工作、复杂度退化、过度分配、I/O 与网络放大、缓存与批量机会、热点路径锁粒度。

只记录有明确性能影响的问题；无则记"性能：无明确问题"。

---

## 步骤 3：安全分路

检查要点见 [references/security.md](references/security.md)。

覆盖：注入、鉴权与越权、不安全反序列化/命令执行、密钥泄露、不安全默认值、信任边界、输入校验缺失。

只记录有真实安全影响的问题；无则记"安全：无明确问题"。

---

## 步骤 4：文档准确性分路

检查要点见 [references/documentation.md](references/documentation.md)。

覆盖：行为变更文档同步、过期注释/示例、公开接口文档缺失、代码与文档不一致。

只记录值得修的问题；无则记"文档：无明确问题"。

---

## 步骤 5：Go 专项检查（仅 Go 项目执行）

> 步骤 0 未检测到 Go 项目时跳过。

检查要点见 [references/go-specialist.md](references/go-specialist.md)。

覆盖：goroutine 生命周期、channel 安全、竞态、context 传递、panic 使用、重试/超时、资源释放、类型断言、Go 规范（命名/import/godoc/Uber style）。

只记录 Go 专项值得处理的问题；无则记"Go 专项：无明确问题"。

---

## 步骤 6：架构专项检查（仅触发时执行）

> 未命中"架构专项触发"时跳过。

检查要点见 [references/architecture.md](references/architecture.md)。

覆盖：分层职责、模块边界、依赖方向、抽象必要性、空概念、核心链路、错误体系、容错、可扩展性、可维护性、性能/安全/测试的架构性风险。

只记录有当前 diff 或必要相邻上下文证据的问题；无则记"架构：无明确问题"。必须区分"必须修复"与"可优化点"，并给出可执行整改方案。

---

## 汇总与去重

执行完所有检查后：

1. 将步骤 1-6 的问题合并
2. 按 (文件, 行) 分组：同一位置多条相似问题合并为一条，注明「本类共 N 处」
3. 对每条候选问题执行反证检查：主动寻找当前 diff 和已读取上下文中能直接推翻其关键事实的证据；存在直接反证时删除，不得用主观解释保留
4. 对照本轮完整 diff 快照清理过期问题：引用行、文件或代码片段不在当前 diff 中的，删除或降级为待确认问题
5. 为每条保留问题定位当前 diff 中最小、连续、逐字匹配的代码范围；优先落在新增行，若问题由新增行触发但表现于相邻上下文，要明确说明触发关系
6. 无法定位到当前快照、依赖未验证仓库外事实、或只有风格偏好的候选问题，删除或降级为待确认问题
7. 去除重叠或低置信项，只保留置信度 `80+` 且值得处理的问题
8. 复核逐文件覆盖清单；存在未披露的 `审查失败`、未处理文件或专项路由遗漏时，不得结束审查
9. 按严重度排序：
   - P0：正确性 bug、安全漏洞、并发严重问题
   - P1：健壮性缺陷、测试缺失、明显性能问题
   - P2：可维护性、文档缺失、规范违反
10. 在结论里补上：范围漂移判定、是否存在文档债务
11. 如果执行了架构专项，在摘要里补上整体架构评分（10 分制）和是否达到生产级标准；评分必须基于本轮 diff 与相邻上下文，不代表全仓库最终评级
12. 如果检查了 ticket/PRD 或可拆分性，在摘要里补上需求合规和可拆分性结论；没有证据时写未检查，不要猜

---

## 输出格式

```text
## 问题
[P0/P1/P2] <标题> - <文件:行> [置信度: 90] [本类共 N 处]
证据: <当前完整 diff 中的证据、触发条件、影响范围>
原因: ...
建议: ...

## 待确认问题
- ...

## 摘要
- <一句话结论>
- diff 快照：<PR/base/head 或本地 diff 范围>
- 文件覆盖：<已审查 N / 仅作上下文 N / 有理由跳过 N / 审查失败 N；列出非零异常项>
- 范围：目标一致 / 范围漂移 / 不完整
- 需求合规：未检查 / 已满足 / 未满足 / 需人工验证
- 可拆分性：未检查 / 不建议拆分 / 建议拆分
- 文档债务：无 / <说明>
- 架构专项：未执行 / <评分>/10，生产级：是/否/需补充证据
```

问题最多 15 条，超出用"其余见 diff，建议本地重点查看"概括。摘要不超过 200 字。无明确问题时写"未发现明确问题"，不强行找瑕疵。

---

## 统一约束

- 验收标准：遵循 `skills/_shared/common-acceptance.md`
- 系统规范：遵循 `home/dot_agents/AGENTS.md`
- 本 skill 额外约束：默认只做分析，不修改文件、不 commit、不 push；仅在用户明确要求发布 GitHub review 时，按 GitHub 发布协议一次性发布；不把主观偏好包装成缺陷
