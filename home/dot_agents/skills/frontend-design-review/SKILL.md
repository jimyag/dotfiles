---
name: frontend-design-review
description: 在实现或审查前端页面、landing page、portfolio、redesign、视觉风格或 UI polish 时使用。适用于先判断页面类型、受众、设计语言和反 AI 默认风格，再给出设计或 review 结论。
---

# 前端设计读题与审查

## 目标

先读清页面的业务语境和审美方向，再设计或审查。避免默认套用 AI 常见模板。

## 何时使用

- landing page、portfolio、品牌页、营销页、redesign
- 用户说页面 AI 味重、不高级、不符合风格
- 有截图、参考站点、品牌资产或已有设计系统
- 需要在动手前判断 UI 应该走什么设计语言

## 何时不要使用

- 纯表单修 bug、数据表格业务逻辑、API 或状态管理问题
- 用户已经给了明确设计稿，只需要按稿实现
- 后台运营/CRM/SaaS 工具只需要密度、层级、可用性检查时，按项目现有设计系统优先

## Design Read

动手前用一句话写清：

```text
Reading this as: <页面类型> for <受众>, with <风格语言>, constrained by <品牌/系统/场景>.
```

先读这些信号：

- 页面类型：landing、portfolio、docs、dashboard、editorial、redesign
- 受众：技术买家、招聘方、消费者、运营人员、内部用户、公共服务用户
- 用户词汇：minimal、premium、serious、playful、editorial、brutalist、trust-first
- 参考信号：截图、URL、竞品、品牌名、已有 logo/color/type/photo
- 安静约束：可访问性、监管、信任、企业采购、移动端、重复使用频率

如果 design read 分叉很大，只问一个会改变方向的问题；能从上下文推断就直接声明并继续。

## Anti-Default Check

除非 brief 明确要求，不要默认使用：

- 紫蓝渐变、发光 mesh、bokeh/orb 背景
- 居中大 hero 加三张 feature card
- 泛 glassmorphism、过量圆角、无意义微动效
- 暗色科技风、Inter + slate 单色调、模板化 SaaS 版式
- 和实际产品/场景无关的 stock-like 氛围图

## 审查重点

- 视觉语言是否服务受众，而不是展示模型审美偏好
- 信息密度是否匹配场景：工具类要可扫读，营销类要有第一屏信号
- 品牌、产品或对象是否在第一视口足够明确
- 文案、按钮、导航和状态是否符合已有产品术语
- 移动端和桌面是否都没有文字溢出、遮挡或布局跳动
- redesign 是否保留应保留的资产和用户习惯，还是无依据地推倒重来

## 输出要求

- 先给 `Design Read`
- 再给 3-5 条最重要的设计判断或修改建议
- 避免泛泛说“更现代”“更高级”；每条建议要能落到布局、层级、颜色、字体、动效、资产或文案
