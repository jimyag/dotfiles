---
name: supabase-postgres-best-practices
description: 在编写、审查或优化 Postgres 查询、数据库结构变更、索引、迁移或数据库配置时使用，尤其适用于基于 Supabase 的项目。
compatibility: 本地 Claude/Codex 配置；按路径激活需要客户端支持非标准的 paths 字段。
when_to_use: 在处理 SQL、迁移、RLS、索引、连接池、查询计划或数据库性能问题，且需要用 Supabase/Postgres 最佳实践指导解决方案时使用。
paths:
  - "**/*.sql"
  - "**/migrations/**"
  - "**/supabase/**"
  - "**/db/**"
license: MIT
metadata:
  author: supabase
  version: "1.1.0"
  organization: Supabase
  date: January 2026
  abstract: 面向 Supabase 和 Postgres 开发者的完整 Postgres 性能优化指南。涵盖 8 类性能规则，按影响从关键项（查询性能、连接管理）到渐进改进项（高级功能）排序。每条规则都包含详细解释、错误与正确的 SQL 示例、查询计划分析和具体性能指标，用于指导自动优化和代码生成。
---

# Supabase Postgres 最佳实践

由 Supabase 维护的完整 Postgres 性能优化指南。规则涵盖 8 类，按影响排序，用于指导自动查询优化和数据库结构设计。

## 适用场景

在以下任务中参考这些指南：
- 编写 SQL 查询或设计数据库结构。
- 实现索引或优化查询。
- 审查数据库性能问题。
- 配置连接池或扩容。
- 优化 Postgres 特有功能。
- 处理行级安全（RLS）。

## 按优先级排列的规则分类

| 优先级 | 分类 | 影响程度 | 前缀 |
|----------|----------|--------|--------|
| 1 | 查询性能 | 关键 | `query-` |
| 2 | 连接管理 | 关键 | `conn-` |
| 3 | 安全与 RLS | 关键 | `security-` |
| 4 | 数据库结构设计 | 高 | `schema-` |
| 5 | 并发与锁 | 中高 | `lock-` |
| 6 | 数据访问模式 | 中 | `data-` |
| 7 | 监控与诊断 | 中低 | `monitor-` |
| 8 | 高级功能 | 低 | `advanced-` |

## 使用方式

阅读各条规则文件中的详细说明和 SQL 示例：

```
references/query-missing-indexes.md
```

每条规则文件包含：
- 简要说明该规则的重要性。
- 错误 SQL 示例及解释。
- 正确 SQL 示例及解释。
- 可选的 EXPLAIN 输出或指标。
- 补充上下文和参考资料。
- Supabase 专项说明（适用时）。

## 参考资料

- https://www.postgresql.org/docs/current/
- https://supabase.com/docs
- https://wiki.postgresql.org/wiki/Performance_Optimization
- https://supabase.com/docs/guides/database/overview
- https://supabase.com/docs/guides/auth/row-level-security
