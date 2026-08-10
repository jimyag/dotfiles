# Pass Strength

Use this before editing. The goal is to avoid the common failure mode where a humanizer makes already-human writing worse.

## Modes

| AI-smell density | Mode | Behavior |
|---|---|---|
| Low | Light | Do not rewrite globally. Fix only obvious artifacts and user-requested issues. |
| Medium | Mixed | Fix strong AI tells, trim padding, preserve original rhythm and quirks. |
| High | Full | Rewrite more aggressively while preserving facts, technical terms, and author stance. |

## Strong Signals

Count only high-confidence signals when choosing mode:

- Chatbot residue: "当然", "希望这有帮助", "let me know", "I'd be happy to", "Here is..."
- Chat UI artifacts: `turn0search0`, `oai_citation`, `:contentReference[...]`, `[web:1]`, `[attached_file:1]`, `contentReference[oaicite`.
- AI-tool URL residue: `utm_source=chatgpt.com`, `utm_source=claude.ai`, `utm_source=copilot.com`, `utm_source=openai`, `referrer=grok.com`, `grok_card`.
- Placeholder leakage: `[INSERT NAME]`, `[YEAR]`, `2025-xx-xx`, `[COMPANY]`.
- Generic positive endings: "未来可期", "值得持续关注", "exciting times ahead".
- Promotional inflation with no evidence: "revolutionary", "seamless", "赋能", "颠覆性".
- Knowledge-cutoff disclaimers or speculative gap filling: "I could not find sources, but they likely maintain a low profile."

Do not count weak signals alone:

- perfect grammar
- formal vocabulary
- em dashes
- curly quotes
- common transition words
- bullet lists in technical content

Clusters matter. Isolated signs do not.

## How to Choose

For short text, judge qualitatively:

- One obvious artifact: light.
- Multiple stock phrases but useful original voice: mixed.
- Most paragraphs are generic, padded, or template-like: full.

For long text, sample the introduction, one middle section, and the ending. If all three are generic, use full mode. If only the ending is generic, edit the ending.

## Mode Rules

### Light

- Keep sentence order unless obviously awkward.
- Fix only strong signals.
- Preserve fragments, parentheticals, roughness, and first-person voice.

### Mixed

- Remove strong signals.
- Shorten padded paragraphs.
- Keep the author's examples, cadence, and opinion.
- Do not normalize every sentence.

### Full

- Rebuild paragraph flow if needed.
- Replace generic claims with specific facts from the source.
- Delete unsupported grand framing.
- Re-check completeness before returning.
