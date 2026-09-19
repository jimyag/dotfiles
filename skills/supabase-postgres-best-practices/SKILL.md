---
name: supabase-postgres-best-practices
description: 在编写、审查或优化 Postgres 查询、schema、索引、迁移、RLS、连接池或数据库配置时使用；先基于版本、schema、查询计划和工作负载选择相关规则，不用于脱离证据的通用 SQL 润色。
license: MIT
compatibility: 需要能够读取目标项目和所选规则文件；查询计划、数据库指标或线上验证需要用户提供的只读访问入口。
metadata:
  author: supabase
  version: "1.1.0"
  organization: Supabase
  date: January 2026
---

# Supabase Postgres 最佳实践

使用 Supabase 维护的 Postgres 规则分析具体数据库问题。规则是决策输入，不替代目标数据库的版本、schema、查询计划、数据规模和真实工作负载。

## 最小流程

1. 明确任务类型：查询性能、连接、RLS、安全、schema、锁、数据访问、监控或高级功能。
2. 读取项目中的 Postgres/Supabase 版本、迁移、schema、索引和相关查询。事实能从项目或只读工具确认时，不向用户重复询问。
3. 只加载与当前任务相关的规则文件；不要一次读取全部 `references/`。
4. 建立当前问题的证据：`EXPLAIN`/`EXPLAIN ANALYZE`、行数和选择性、现有索引、锁等待、连接池状态、RLS policy 或可复现输入。
5. 给出最小建议，说明它解决的瓶颈、引入的写放大/存储/锁/兼容性代价，以及不适用条件。
6. 用户要求修改时，沿用项目现有迁移方式实现，并运行与风险相称的静态、计划或运行时验证。

缺少查询计划、真实基数或版本信息时，可以指出高概率问题和下一步观测方式，但不要声称已经证明性能收益。

## 规则路由

| 任务 | 读取的规则 |
| --- | --- |
| 慢查询、索引选择 | `references/query-*.md`、必要时 `references/monitor-explain-analyze.md` |
| 连接数、池化、超时 | `references/conn-*.md` |
| RLS、权限和授权边界 | `references/security-*.md` |
| 类型、约束、主外键、分区 | `references/schema-*.md` |
| 死锁、长事务、任务领取 | `references/lock-*.md` |
| 分页、批量写入、upsert、N+1 | `references/data-*.md` |
| 统计信息、vacuum、运行时诊断 | `references/monitor-*.md` |
| JSONB、全文检索等专项能力 | `references/advanced-*.md` |

若多个分类同时适用，先处理能决定正确性的约束和安全问题，再处理性能优化。

## 证据与安全边界

- 不凭 SQL 形状断言索引一定有效；同时检查谓词、数据分布、现有索引、排序、连接条件和写入成本。
- `EXPLAIN ANALYZE` 会实际执行语句。对写操作、长查询或生产负载，未获得明确授权时只使用安全的计划入口或给出待执行命令。
- RLS 优化不得弱化授权语义。分别验证允许访问、拒绝访问和常见查询路径。
- schema 与索引迁移要说明锁影响、回滚、并发创建能力、历史数据处理和部署顺序；不要假设所有 Postgres/Supabase 版本行为相同。
- 不把一次本地计划或小数据集耗时推广成生产收益；保留环境、数据规模和缓存状态。
- 不执行线上写入、删除、`VACUUM FULL`、扩容或配置变更，除非用户明确授权目标和范围。

## 输出契约

返回内容至少包括：

1. **结论**：最可能的问题或推荐方向。
2. **证据**：版本、schema、查询计划、指标或源码位置；缺失证据单独列出。
3. **建议**：SQL、索引、migration 或配置改动，以及选择了哪些规则。
4. **代价与边界**：锁、写入、存储、RLS、兼容性和不适用情形。
5. **验证**：可单独执行的检查、预期计划变化或运行指标。

只做审查时不修改文件；用户要求实现时，报告实际修改、执行过的验证和仍未验证的运行面。

## 官方资料

规则之外需要确认版本语义时，优先使用：

- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
