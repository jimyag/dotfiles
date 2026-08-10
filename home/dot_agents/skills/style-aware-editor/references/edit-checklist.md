# Edit Checklist

Use this before returning the final rewrite.

## Accuracy

- Facts, numbers, names, commands, code, and citations are unchanged unless the user asked to change them.
- No invented examples, benchmarks, or personal anecdotes.
- Unverified claims are either removed or marked as needing verification.
- The rewrite is not truncated. All source sections are either preserved, intentionally compressed, or explicitly omitted with explanation.
- Direct quotes, code, URLs, file paths, identifiers, and citation markers are intact unless the user asked to edit them.
- Protected spans were identified before editing.
- Material source points are still covered unless the user asked to compress.

## Voice

- The rewrite matches the text type.
- It does not blindly become casual.
- It keeps the author's stance where the original had one.
- It avoids over-polishing personal or opinionated writing.
- It preserves register: academic stays academic, technical stays precise, PR text stays compact.
- It does not strip human signs such as specific detail, uneven rhythm, self-correction, or first-person experience.

## AI Smells

- No chatbot residue: "当然", "希望这有帮助", "let me know", "let's dive in".
- No copied chat artifacts: fake citations, placeholder fields, or assistant meta-prompts.
- No AI-tool URL residue such as `utm_source=chatgpt.com`, `utm_source=claude.ai`, or `referrer=grok.com`.
- No cutoff disclaimers or speculative gap filling.
- No generic positive ending.
- No inflated significance unless supported.
- No vague authorities.
- No forced rule-of-three structure.
- No excessive bold labels, emojis, or decorative formatting.
- No conclusion section unless it adds information.
- No false agency or lecturer voice unless the genre needs it.
- No repeated paragraph shape such as "claim + explanation + abstract wrap-up" across several adjacent paragraphs.

## Readability

- Paragraphs start with substance, not warm-up sentences.
- Lists are used only when they improve scanning.
- Sentence rhythm is varied but not deliberately quirky.
- Technical terms are consistent. No synonym cycling.
- Markdown structure serves the reader. It is not decorative.

## Final Pass

Ask silently: "What still makes this sound like generated text?"

Fix only the remaining high-signal issues. Do not keep rewriting until the text loses its meaning or voice.

For `detect` mode, confirm that no rewrite was included. For `edit` mode, confirm that quoted text, code blocks, and attributed material were not silently changed.
