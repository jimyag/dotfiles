# Advanced AI Writing Patterns

Use this only for deep audits, English marketing/social/blog prose, or when the user asks to find subtle AI-writing tells. These are writing-quality signals, not authorship proof.

## Contents

- High-Confidence Publishing Bugs
- Vocabulary Tiers
- Structural Patterns
- Social and Promotional Patterns
- Chinese High-Priority Patterns
- What Not to Over-Correct

## High-Confidence Publishing Bugs

Fix or flag these first:

- Chat artifacts: `turn0search0`, `oai_citation`, `:contentReference[...]`, `[web:1]`, `[attached_file:1]`, JSON-shaped source payloads.
- AI-tool URL residue: `utm_source=chatgpt.com`, `utm_source=claude.ai`, `utm_source=copilot.com`, `utm_source=openai`, `referrer=grok.com`, `grok_card`.
- Placeholder leakage: `[INSERT NAME]`, `[YEAR]`, `[COMPANY]`, `[TODO]`, `2025-xx-xx`.
- Cutoff disclaimers: "as of my last update", "I don't have access to real-time information".
- Speculative gap filling: "specific details are limited, but they likely...", "appears to have maintained a low profile".

Do not invent replacement facts. Remove the artifact, or ask for the missing source data.

## Vocabulary Tiers

### Always Question

These often substitute style for substance:

- `delve`, `deep dive`, `unpack`
- `landscape` as a metaphor
- `realm`, `paradigm`, `tapestry`, `beacon`
- `testament to`, `serves as`, `stands as`
- `robust`, `comprehensive`, `cutting-edge`
- `leverage`, `utilize`, `pivotal`, `seamless`
- `boasts`, `features` as inflated verbs
- `at its core`, `best practices`, `game-changer`

Default fix: use a plain verb or state the concrete fact.

### Flag in Clusters

One of these can be normal. Two or more in the same paragraph usually means the paragraph needs tightening:

- `harness`, `navigate`, `foster`, `elevate`, `empower`
- `streamline`, `bolster`, `spearhead`, `facilitate`
- `ecosystem` as a metaphor
- `myriad`, `plethora`, `multifaceted`
- `transformative`, `cornerstone`, `paramount`
- `poised`, `burgeoning`, `nascent`, `overarching`

### Flag by Density

These are normal words, but a dense cluster turns into vague praise:

- `significant`, `innovative`, `effective`, `scalable`
- `compelling`, `unprecedented`, `exceptional`
- `sophisticated`, `instrumental`, `world-class`

Replace with numbers, named constraints, observed behavior, or remove the claim.

## Structural Patterns

Watch for these shapes:

- False contrast: "not X but Y", "this is not about X, it is about Y".
- Hollow intensifiers: `real`, `actual`, `genuine`, `true` attached to abstract nouns without naming the contrast.
- Vague endorsement: "worth reading", "worth exploring", "worth paying attention to".
- Hedge stacking: "could potentially", "may eventually", "might ultimately".
- Generic future closer: "could become one of the defining trends", "is poised to become the next major chapter".
- Missing bridges: paragraphs can be rearranged without changing meaning.
- Rule-of-three compulsion: every claim becomes "A, B, and C".
- Bare-noun bullet lists: five or more short bullets with no verbs and the same grammar shape.
- Synonym cycling: rotating terms like "developers", "builders", "practitioners" to avoid repeating the clearest word.
- Inline label prose: every sentence starts with a bold or title-cased label instead of flowing naturally.
- Hyphenated-pair overuse: "developer-friendly", "production-ready", "cloud-native", "AI-powered" stacked without evidence.
- False agency: inanimate things doing human actions, such as "the decision emerges", "the data tells us", "the market rewards".
- Rhetorical setup: "here's what I mean", "think about it", "this is why", "what makes this hard is".
- Dramatic fragmentation: "X. That's it.", "Not A. Not B. C.", repeated staccato fragments for manufactured weight.
- Lazy extremes: `always`, `never`, `everyone`, `nobody`, `the only`, used without a concrete scope.

Fix by naming the specific claim, cutting the wrapper, or adding the missing connective sentence.

## Social and Promotional Patterns

These matter mainly in LinkedIn, X, launch posts, investor updates, and marketing pages:

- Hashtag stuffing: six or more hashtags, especially broad category tags.
- Notability name-dropping without a reason the reader should care.
- Tourism language: "nestled", "bustling", "vibrant", "thriving" without concrete detail.
- Superficial `-ing` clauses: "showcasing", "highlighting", "underscoring", "reflecting" after a sentence that already made the point.

## Chinese High-Priority Patterns

For Chinese prose, prioritize these before word-by-word cleanup:

- 协作口吻：`接下来我们`、`我们先来看`、`下面我们`、`希望这能帮助你`。
- 讲义动作：`拆一拆`、`盘一盘`、`捋一捋`、`聊一聊`、`划重点`。
- 路标词堆叠：`更关键`、`更要命`、`换句话说`、`事实上`、`值得注意`、`与此同时`。
- 二分对照壳：`不是 A 而是 B`、`不在于 A 而在于 B`、`并非 A 而是 B`。
- 条件句堆叠：`一旦...就...`、`只有...才...`、`无论...都...`、`通过...来...`。
- 戏剧化揭露：`遮羞布`、`面具`、`外衣`、`揭开真面目`、`戳穿真相`。
- 伪学术腔：`底层逻辑`、`宏大叙事`、`舆论场`、`赛道`、`闭环`、`抓手`。
- 段落同构：连续三段都是“观点句 + 解释 + 段尾总结”。
- 段尾抽象收束：每段都补一句“这说明 / 这意味着 / 本质上”。

Fix structure first, then tone, then sentence patterns, then vocabulary. Do not mechanically replace words while leaving the paragraph shape intact.

## What Not to Over-Correct

Do not flag these by themselves:

- Em dashes in finished prose.
- Curly quotes in documents, blogs, or locale-aware writing.
- Passive voice in academic, legal, or formal technical writing.
- Bullets in specs, checklists, changelogs, API docs, or PR descriptions.
- Repeated technical terms where synonym cycling would reduce clarity.
- Formal vocabulary required by the audience.

When the pattern is plausible but not decisive, mark it as context-dependent instead of rewriting aggressively.
