---
name: eli5
description: 像给 5 岁孩子讲解一样解释一个主题。在用户输入 /eli5 加主题，或要求用极简单的图解说明事物原理时使用。
license: Apache-2.0
---

# 通俗图解

面向完全不了解该主题的读者，解释用户当前请求中的主题。默认生成自包含的 HTML 图解，使用大幅图片和极少文字。

不要依赖 `$ARGUMENTS` 等特定客户端的参数占位符。如果用户要求其他格式，在该格式中保持同样简单、以视觉为主的教学方式。

## 来源

基于 Anthropic 的 `claude-plugins-community/eli5`，提交为 `f4c9452f5ca091f1be7064d9faab1b001ea21645`，改编为可跨客户端使用的 Agent Skills。上游技能作者为 Thariq Shihipar。本版本移除了 Claude 专用的 `$ARGUMENTS` 依赖。
