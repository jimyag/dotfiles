---
name: style-aware-editor
description: Use when auditing or editing Chinese or English writing that sounds AI-generated, robotic, generic, over-polished, template-like, or mismatched to the target article type; also use for precise Chinese technical, API, product, UI, operational, or troubleshooting copy that must preserve facts and machine-readable content.
---

# Style Aware Editor

## Purpose

Edit writing so it sounds natural for its target context, not merely "more casual". Preserve facts, technical terms, structure that serves the reader, and the author's actual stance.

Treat AI-writing patterns as quality signals, not proof of authorship. Do not use this skill to make consequential claims about who wrote a text.

## When to Use

Use for:

- Text that feels like AI wrote it: generic, padded, evenly structured, over-explained, or full of stock phrases.
- Drafts that need to match a target article type: technical tutorial, engineering note, opinion piece, incident review, PR/issue text, product update, or personal blog.
- Chinese technical, API, product, UI, operational, or troubleshooting copy that needs fact-preserving terminology, status wording, steps, or error recovery guidance.
- Requests like "降低 AI 味", "写得自然点", "别像 ChatGPT", "humanize this", "make this less robotic", "detect AI patterns", "flag only", "scan this", "按我的文风改".

Do not use for:

- Pure fact checking without rewriting.
- Legal, medical, or policy text where exact wording matters more than style.
- Rewriting to hide authorship or evade an explicit disclosure requirement.
- 中文内部技术方案、评审稿、架构说明等需要重构论证路径的长文；那类场景优先 `technical-writing`。

## Workflow

1. Confirm there is actual source text to edit. If there is no text yet, stop and ask for it.
2. Choose the operation mode:
   - `rewrite`: default; audit briefly, then return revised text.
   - `detect`: flag AI-writing patterns only, with no rewrite. Use when the user says "detect", "flag only", "audit only", "scan", or similar.
   - `edit`: modify a named file in place. Use minimal, targeted edits and verify afterward.
   - `review`: review a document and return flagged sections or recommendations.
3. Identify the text type and target reader.
4. If the text is a Chinese internal technical design, review note, or architecture writeup, switch to `technical-writing`.
5. If the user provides sample writing, infer voice from it before editing.
6. Mark protected spans before editing: quotes, code, commands, file paths, identifiers, citations, required terminology, and attributed text.
7. For Chinese technical documentation, API/status copy, product/UI copy, operational steps, or troubleshooting, read [chinese-technical-copy.md](references/chinese-technical-copy.md).
8. Choose scene and edit scope. Read [scene-scope-and-voice.md](references/scene-scope-and-voice.md) when the text is long, Chinese, or has strict preservation requirements.
9. Run a pre-flight pass-strength check. Read [pass-strength.md](references/pass-strength.md) for light / mixed / full mode.
10. Scan for AI-writing smells. Read [ai-writing-smells.md](references/ai-writing-smells.md) when doing a serious pass.
11. For English marketing, social, blog, or deep audit requests, also read [advanced-ai-patterns.md](references/advanced-ai-patterns.md).
12. Pick the style profile and register. Read [style-profiles.md](references/style-profiles.md) when the article type is not obvious.
13. Edit in passes:
   - remove padding and chatbot artifacts
   - replace generic claims with specific facts or delete them
   - vary rhythm without making the writing performative
   - restore author stance where appropriate
   - preserve technical precision
14. Run the final checklist from [edit-checklist.md](references/edit-checklist.md).

For longer files, optionally run:

```bash
python3 scripts/scan-ai-smells.py <file>
```

Use the script output as hints, not as a verdict.

## Style Selection

Choose the profile before editing:

| Text type | Default editing stance |
|---|---|
| Technical tutorial | Clear, direct, exact. Keep steps. Cut hype and filler. |
| Engineering practice | Keep tradeoffs and constraints. Strengthen concrete judgment. |
| Academic / formal technical | Preserve register, hedging, citations, passive voice, and domain terms. |
| Opinion / commentary | Make the stance visible. Remove fake balance. |
| Incident review | Factual, time-ordered, accountable. No dramatic language. |
| PR / issue / changelog | Short, concrete, reviewer-friendly. No marketing language. |
| Personal blog | Keep personal rhythm. Avoid corporate polish. |

If unsure, ask one concise question: "这篇是教程、观点文、复盘，还是 PR/issue 文案？"

## Editing Rules

- Meaning first, style second. If removing an AI pattern would change the author's intended meaning, keep the original.
- Preserve conditions, exceptions, units, defaults, compatibility, failure handling, and certainty markers such as `可能`, `建议`, `通常`, and `预计`.
- Distinguish human actions from automatic system behavior; do not turn system outcomes into extra user steps.
- Edit in place by default. Do not silently reorder sections, merge paragraphs, or rewrite the structure unless the user asks.
- In `detect` mode, separate clear problems from context-dependent patterns. Do not rewrite.
- In `edit` mode, change only the flagged spans. Leave already-human paragraphs untouched.
- Do not edit quoted material, code blocks, or text attributed to someone else unless the user explicitly asks. Flag issues there instead.
- For large files, confirm the target section before broad edits.
- Preserve coverage. If the source has five material points, the rewrite must still cover those five points unless the user asked to compress.
- Do not delete whole sentences in long Chinese public-writing by default. Put empty sentences in a deletion suggestion list unless the user allowed structural rewriting.
- For release notes, launch copy, changelog text, issue/PR prose, or product claims, ground wording in the actual artifact, diff, screenshot, or source text instead of inventing generic polish.
- Keep facts and code exact. Do not invent names, numbers, citations, benchmark results, or anecdotes.
- Prefer concrete nouns and verbs over abstract framing.
- Delete empty transitions instead of replacing them with other empty transitions.
- Keep useful repetition. Do not synonym-cycle technical terms.
- Avoid turning every paragraph into a three-part structure.
- Remove chatbot residue: "当然", "希望这有帮助", "让我们深入探讨", "值得注意的是", "总而言之", "in conclusion", "let me know".
- Remove copied chat UI artifacts: fake citations, placeholder fields, meta-prompts, and leftover assistant instructions.
- Treat em dashes, curly quotes, passive voice, and formal vocabulary as weak signals. Fix them only when the context makes them harmful.
- Do not over-edit human-first drafts. Fragments, mixed feelings, self-corrections, and uneven rhythm can be evidence of real voice.
- For Chinese technical writing, prefer short judgment sentences over slogan-like summaries.
- For English technical writing, prefer plain verbs: use, is, has, shows, fails, returns.
- Preserve the author's intentional tone even when it is blunt, narrow, or opinionated.
- Add personality only when the genre calls for it. Do not inject first-person emotion into docs, PRs, incident reports, or formal technical writing.
- If the user asks for repeated cleanup, cap automatic rewrite passes at two. More passes usually erase voice faster than they remove real problems.

## Special Modes

### Document Review

Use when the user asks to review a document rather than fully rewrite it.

- Check for placeholder text, broken references, copied chat artifacts, and obvious privacy leakage.
- For bilingual text, verify terminology and meaning stay aligned.
- Return the reviewed text or flagged sections, not a broad essay about writing.

### Paragraph Coherence

Use when the ask is mainly "顺不顺" or "连不连贯", not full rewriting.

1. Check whether each paragraph follows from the previous one.
2. Flag abrupt topic shifts and monotone rhythm.
3. Suggest the smallest viable fix: a bridge phrase, one reordered clause, or one sentence move.

## Output

For short text, return:

1. Revised text

For detect-only mode, return:

1. Findings grouped by severity
2. The exact phrase or pattern
3. Why it matters, including false-positive context when relevant

For long text or file edits, return:

1. Revised sections or applied changes
2. Remaining risks: facts needing verification, places where style depends on user preference
3. Optional smell summary if useful

Do not over-explain every sentence-level edit unless the user asks. If the user asked only for the rewrite, stop after the edited text.

## Stop Conditions

Stop and ask before rewriting if:

- The target audience or article type changes the style substantially.
- The rewrite would require adding facts, examples, or citations not present in the source.
- The text is contractual, legal, regulatory, or compliance-sensitive.
