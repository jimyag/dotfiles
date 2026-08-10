# PR 文案规则

创建或更新 PR 时，先读取真实 base/head、commit、diff、验证结果和仓库 PR 模板。模板存在时保留其结构并填写适用字段；未知验证结果写“未验证”。

## 标题

- 准确表达核心行为变化，避免 `update`、`fix bug`、`changes`、`WIP` 等泛化标题。
- 仓库明显使用 Conventional Commits 时沿用相同风格。
- issue 编号不能牺牲标题可读性。

## 语言

按用户指定、显式语言参数、相关 commit 的主要语言、仓库近期提交语言依次判断。PR 模板有固定语言时优先保持模板语言。

## Body

- 基于真实 diff 总结背景、关键改动、验证和风险，不照抄 commit 列表。
- 存在关联 issue 或 ticket 时，必须在标题或 body 中明确引用。
- 明确 breaking change、迁移、配置变化和 reviewer 应优先查看的模块。
- 混有机械改动时区分噪音与核心逻辑；PR 过大且难以概括时明确建议拆分，不用文案掩盖审查成本。
- 无模板时使用以下最小结构：

```markdown
## 摘要

<解决的问题和总体改动>

## 关键改动

- <关键改动>

## 验证

- <验证命令与结果，或未验证>

## 备注

- <风险、兼容性、迁移或 reviewer 关注点；没有可省略>
```

## 模板查找

```bash
rg --files . .github | rg 'pull_request_template|PULL_REQUEST_TEMPLATE'
```
