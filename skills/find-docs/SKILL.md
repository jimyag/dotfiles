---
name: find-docs
description: 在需要查询第三方库、框架、SDK、API 的最新官方文档、示例或版本差异时使用。适用于写代码前确认接口、排查文档细节、或担心知识过期的场景。
---

# 查询最新文档

## 目标

通过 Context7 查询最新文档和代码示例，避免依赖过期记忆。

## 何时使用

- 需要确认库或框架的最新 API
- 要看官方示例
- 用户问某个库怎么用
- 你怀疑训练数据可能过期

## 何时不要使用

- 问题完全不依赖第三方库
- 仓库里已经有足够明确的本地实现可参考

## 基本流程

1. 先从项目文件识别技术栈和版本，例如 `package.json`、`go.mod`、`pyproject.toml`、`Cargo.toml`、`Gemfile`
2. 先用 `npx ctx7@latest library` 解析库 ID
3. 再用 `npx ctx7@latest docs` 查询具体问题
4. 用最相关的官方文档结果回答

## 常用命令

```bash
npx ctx7@latest library react "useEffect cleanup async"
npx ctx7@latest docs /facebook/react "useEffect cleanup async"
```

如果用户已经明确提供了 Context7 的库 ID，例如 `/facebook/react`，可以直接查 `docs`。

## 查询规则

- query 要具体，不要只写一个单词
- 尽量直接使用用户原问题
- 不要在 query 里带敏感信息
- 单次问题尽量不要超过 3 次查询
- 框架、SDK、云服务、CLI 或 API 行为依赖版本时，先确认项目版本；版本缺失且会影响答案时再问用户
- 优先级：官方文档 > 官方 changelog/blog > 标准文档/MDN > 仓库源码；不要把博客、问答站或 AI 摘要当 primary source
- 如果本地仓库已有相同模式，先读本地实现；官方文档用于确认当前版本语义，不替代项目约定

## 输出要求

- 说明查的是哪个库/版本
- 给出结论时尽量带简短示例
- 若文档和你原本记忆冲突，以文档为准
- 若遇到配额错误，明确说明并建议运行 `npx ctx7@latest login` 或设置 `CONTEXT7_API_KEY`
- 对实现建议说明依据来自官方文档、本地现有模式，还是二者共同支持
