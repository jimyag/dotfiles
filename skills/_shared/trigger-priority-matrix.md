# 触发优先级矩阵（Single Source of Truth）

维护说明：本文件只处理 skill 之间的优先级冲突；每个 skill 的触发条件仍由其 frontmatter 维护。

## 优先级顺序

当用户请求可能匹配多个 skill 时，按以下顺序决策（编号越小优先级越高）：

1. Codecov 覆盖率查询或 gate 失败 -> `codecov-coverage`
2. 代码审查、发起 review -> `requesting-code-review`
3. agent 配置、skills、hooks、MCP 健康审计 -> `agent-health`
4. 规范化提交 -> `git-commit`

## 补充路由规则

- 中文内部技术方案、设计说明、架构说明、评审稿 -> `technical-writing`
- 通用改稿、去 AI 味、润色、文风贴合 -> `style-aware-editor`
- “以前是好的现在坏了”“同样症状还在”“截图回归” -> `systematic-debugging`
- “有没有必要做/保留/继续” -> `brainstorming`
- 前端页面、redesign、视觉风格、UI AI 味 -> `frontend-design-review`
- 查询外部 skill、判断是否值得引入 -> `find-skills`
- 任务已经明确但步骤较多 -> `writing-plans`
- 架构决策记录、ADR、decision record、记录“为什么这么选” -> `architecture-decision-record`
- 带 GitHub URL 且用户只要 issue/PR/repo 内容 -> 使用当前可用的 GitHub connector 做只读获取，不额外路由到 skill
- GitHub Actions 失败 -> 使用当前可用的 GitHub connector 获取 run/job/step/log；需要持续修复到全绿时使用 `loop-on-ci`
- `codecov/project`、`codecov/patch`、flag 或 component 失败 -> `codecov-coverage`

## 常见歧义

- `loop-on-ci` vs `systematic-debugging`：持续跟进 GitHub Actions 选前者；本地测试或普通代码异常选后者
- `loop-on-ci` vs `codecov-coverage`：GitHub Actions job 失败选前者；Codecov coverage gate 失败选后者
- `style-aware-editor` vs `technical-writing`：调文风选前者，重构技术论证选后者
- `requesting-code-review` vs `systematic-debugging`：检查改动质量选前者，排错误根因选后者
- `frontend-design-review` vs `systematic-debugging`：设计方向、视觉质量、AI 味选前者；行为错误、回归、交互失效选后者
- `agent-health` vs `requesting-code-review`：AGENTS/skills/hooks/MCP/验证命令漂移选前者；业务代码 diff 审查选后者
- `brainstorming` vs `writing-plans`：先判断方向和取舍选前者，方向已定后拆步骤选后者
- `brainstorming` vs `architecture-decision-record`：还在比较方案选前者；已经形成会约束未来实现的决策、需要记录“为什么”选后者
- `writing-plans` vs `architecture-decision-record`：拆实施步骤和验证选前者；沉淀长期设计选择、备选方案和代价选后者
- `technical-writing` vs `architecture-decision-record`：写面向读者的设计说明选前者；写结构化 ADR 文件选后者

## 冲突决策规则

- 用户显式指定 skill 名称时，忽略本矩阵，直接执行指定 skill。
- 用户请求同时匹配多个 skill 时，按上表优先级选择最高者。
- 若用户请求明确包含两个独立任务（如"先分析 CI 失败，再整理发布 issue"），按顺序依次执行对应 skill。
- 未明确匹配或模糊请求（兜底）：优先拒绝自动执行修改类或部署类操作，应向用户提问确认意图，或默认使用当前可用 connector 获取只读上下文。

## 各 skill 的「何时不要使用」职责边界

各 skill 的 `Do NOT use` 段落必须与本矩阵一致：

- `codecov-coverage`：不处理普通 GitHub Actions job、本地测试失败或功能实现。
- `loop-on-ci`：不处理一次性状态查询、纯 Codecov gate 或没有 PR 的本地失败。
- `agent-health`：不处理业务代码 review、应用 bug 根因排查或功能实现。
- `frontend-design-review`：不处理纯业务逻辑、API、CI、非 UI bug；已有明确设计稿时不替代按稿实现。
- `git-commit`：不处理代码分析/评审、部署；工作区无变更或用户仅需建议时不触发。
- `architecture-decision-record`：不处理开放式方案探索、普通计划拆解、单点 bugfix、机械迁移或没有真实备选方案的既有约定。
