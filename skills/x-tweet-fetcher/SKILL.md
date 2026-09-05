---
name: x-tweet-fetcher
description: 研究需要抓取 X 推文、回复串、时间线、文章或中文社交平台内容时使用。
compatibility: 需要 Python 3.10+ 和 uv。回复、时间线、渲染页面和内容发现还需要运行中的 Camofox 服务与网络访问。
---

# X 推文抓取

无需官方 API 即可抓取 X 和多个中文平台的内容。单条推文优先使用零依赖方式；仅在任务需要回复、时间线、渲染页面或内容发现流程时切换到 Camofox 模式。

## 选择方式

- 单条公开推文：使用零依赖抓取方式。
- 回复、用户时间线、X 列表、监控：使用 Camofox 方式。
- 微信、微博、哔哩哔哩、CSDN 等渲染页面：使用 `fetch_china.py`。
- 浏览器模式不可用时明确说明，不要假装已完成更完整的抓取。

## 技能中的实际脚本

- `scripts/fetch_tweet.py`：X 推文、回复、时间线、文章、列表和监控。
- `scripts/fetch_china.py`：中文平台内容抓取。
- `scripts/camofox_client.py`：共享的浏览器客户端和搜索辅助工具。
- `scripts/x_discover.py`：面向内容发现的工作流。

## 补充资源

- 实际命令示例和正确脚本名见 [使用说明](references/usage.md)。
- Camofox 安装和健康检查见 [Camofox 配置](references/camofox-setup.md)。
- 输出结构和已知限制见 [输出与行为](references/output-and-behavior.md)。

## 操作规则

- 从能够回答问题且成本最低的方式开始。
- 缺少浏览器证据时，不要宣称已覆盖回复、时间线或渲染页面。
- 汇总抓取内容时保留来源 URL 和关键元数据。
- 说明平台限制，例如需要登录的 X 文章或受到限流的渲染页面。

## 输出要求

- 说明使用的模式：零依赖、Camofox 或中文平台抓取。
- 提供抓取文本或摘要，并附来源 URL。
- 说明重要缺口，例如缺少回复、文章不完整或登录限制。
