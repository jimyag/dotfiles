# 触发优先级矩阵（Single Source of Truth）

维护说明：本文件只处理 skill 之间的优先级冲突；每个 skill 的触发条件仍由其 frontmatter 维护。

## 优先级顺序

当用户请求可能匹配多个 skill 时，按以下顺序决策（编号越小优先级越高）：

1. CI 失败根因分析 -> `ci-analyze`
2. GitHub 内容解读（issue/PR/repo/discussion） -> `gh-view`
3. 代码审查、发起 review -> `requesting-code-review`
4. agent 配置、skills、hooks、MCP 健康审计 -> `agent-health`
5. 规范化提交 -> `git-commit`

## 补充路由规则

- 中文内部技术方案、设计说明、架构说明、评审稿 -> `technical-writing`
- 通用改稿、去 AI 味、润色、文风贴合 -> `style-aware-editor`
- “以前是好的现在坏了”“同样症状还在”“截图回归” -> `systematic-debugging`
- “有没有必要做/保留/继续” -> `brainstorming`
- 前端页面、redesign、视觉风格、UI AI 味 -> `frontend-design-review`
- 查询外部 skill、判断是否值得引入 -> `find-skills`
- 任务已经明确但步骤较多 -> `writing-plans`
- 架构决策记录、ADR、decision record、记录“为什么这么选” -> `architecture-decision-record`
- 带 GitHub URL 且用户要先读 issue/PR/repo 内容 -> `gh-view`

## 常见歧义

- `gh-view` vs `ci-analyze`：看内容选 `gh-view`，查失败根因选 `ci-analyze`
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
- 未明确匹配或模糊请求（兜底）：优先拒绝自动执行修改类或部署类操作，应向用户提问确认意图，或默认降级为只读操作（如调用 `gh-view` 获取上下文）。

## 各 skill 的「何时不要使用」职责边界

各 skill 的 `Do NOT use` 段落必须与本矩阵一致：

- `ci-analyze`：不处理功能实现、部署、发布。
- `gh-view`：不处理代码修改、CI 根因分析（优先 ci-analyze）、代码审查（优先 requesting-code-review）。
- `agent-health`：不处理业务代码 review、应用 bug 根因排查或功能实现。
- `frontend-design-review`：不处理纯业务逻辑、API、CI、非 UI bug；已有明确设计稿时不替代按稿实现。
- `git-commit`：不处理代码分析/评审、部署；工作区无变更或用户仅需建议时不触发。
- `architecture-decision-record`：不处理开放式方案探索、普通计划拆解、单点 bugfix、机械迁移或没有真实备选方案的既有约定。
