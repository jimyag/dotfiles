# AI Writing Smells

Use this as an editing checklist, not as a detector. A single smell is not proof of AI writing. Clusters are what matter.

## Contents

- Content Smells
- Language Smells
- Formatting Smells
- False Positives

## Content Smells

### Chat UI artifacts

These are high-confidence signs that text was copied from an assistant UI:

- `turn0search0`, `citeturn0search0`, `oai_citation`, `:contentReference[...]`
- `[web:1]`, `[attached_file:1]`, JSON-shaped attribution payloads
- `utm_source=chatgpt.com`, `utm_source=claude.ai`, `utm_source=copilot.com`, `utm_source=openai`, `referrer=grok.com`, `grok_card`
- meta-prompts like "Would you like me to convert this to..."
- placeholder leakage: `[INSERT NAME]`, `[YEAR]`, `[COMPANY]`, `2025-xx-xx`
- cutoff disclaimers or speculative filler: "as of my last update", "I don't have access to real-time information", "specific details are limited, but..."

Fix: remove artifacts. If they were meant to be citations or fields, replace only with real source data the user provided.

### Significance inflation

Watch for:

- "具有重要意义"
- "标志着关键一步"
- "体现了重要性"
- "stands as / serves as"
- "pivotal / crucial / vital"
- "broader trend / evolving landscape"

Fix: say what happened or what the thing does. Delete grand framing unless the text proves it.

### Promotional language

Watch for:

- "强大 / 优雅 / 无缝 / 革命性 / 颠覆性"
- "vibrant / robust / seamless / groundbreaking / world-class"
- "赋能 / 打造 / 助力 / 全方位"

Fix: replace praise with observable behavior, constraints, numbers, or examples.

### Vague authority

Watch for:

- "业内人士认为"
- "有研究表明"
- "一些专家指出"
- "industry reports suggest"
- "experts argue"

Fix: name the source, or remove the claim.

### Template balance

Watch for:

- "既有优势，也有挑战"
- "不是 X，而是 Y"
- "not just X, but Y"
- "on the one hand / on the other hand" when the contrast is fake

Fix: keep the actual tradeoff. Remove rhetorical symmetry.

### Generic positive ending

Watch for:

- "未来可期"
- "值得持续关注"
- "这只是开始"
- "exciting times ahead"

Fix: end with a concrete consequence, next step, or open question.

## Language Smells

### Stock transitions

Common Chinese stock phrases:

- 首先 / 其次 / 最后 when not needed
- 值得注意的是
- 总的来说
- 换句话说
- 从某种意义上说
- 不难看出
- 可以发现

Common English stock phrases:

- let's dive in
- it is important to note
- in today's fast-paced world
- at its core
- the key takeaway
- in conclusion
- here is what you need to know
- the real question is

Fix: delete the phrase and start with the substance.

### Claude-style markdown overuse

Watch for:

- short text split into many headings
- bullets for continuous thought
- random bold labels inside ordinary prose
- numbered lists where order does not matter
- post-action summaries: "To recap", "In summary", "Here's what was covered"

Fix: collapse structure when prose is clearer. Keep lists where scanning matters.

### Superficial "-ing" / "通过...从而..."

Watch for:

- "highlighting / underscoring / showcasing / reflecting"
- "通过 X，从而 Y" where Y is vague

Fix: split into concrete cause and effect, or delete the tail.

### Copula avoidance

Watch for:

- "serves as"
- "stands as"
- "boasts"
- "features"
- "充当了"
- "构成了"

Fix: use "is", "has", "是", "有" when that is clearer.

### Over-neat rhythm

Watch for:

- every paragraph has the same length
- every list has exactly three items
- every section starts with a generic opener
- sentences all land at the same level of certainty
- 连续三段都是“观点句 + 解释 + 段尾总结”
- every paragraph ends with a quotable one-liner

Fix: vary length naturally. Shorten where the idea is simple. Let important details take more space.

### False agency and lecturer voice

Watch for:

- "the data tells us"
- "the market rewards"
- "the decision emerges"
- "this is why"
- "here's what I mean"
- "think about it"
- `下面我们` / `我们先来看` / `接下来我们`

Fix: name the actor, or start with the actual claim. Avoid putting the reader in a classroom unless the piece is explicitly a lesson.

## Formatting Smells

- Horizontal rule `---` before every heading.
- ALL CAPS headings in ordinary docs.
- Excessive bold labels in lists.
- Emojis used as emphasis in serious writing.
- Title Case headings in ordinary technical docs.
- Too many bullets where prose would be clearer.
- One-line paragraph that repeats the heading before saying anything.

Fix: remove decorative emphasis. Keep structure only when it helps scanning.

## False Positives

Do not flag these by themselves:

- perfect grammar
- formal vocabulary
- em dashes
- curly quotes
- common transition words used sparingly
- passive voice in academic, legal, or formal technical writing
- bullet lists in docs, specs, PR descriptions, or checklists

Preserve these human-writing signs:

- specific names, places, tools, constraints, and dates
- mixed feelings or bounded confidence
- parenthetical self-corrections
- uneven sentence length
- first-person details when the text is a personal blog, retrospective, or field note

When in doubt, preserve the original voice and edit less.

For deep audits or English marketing/social prose, continue with [advanced-ai-patterns.md](advanced-ai-patterns.md).
