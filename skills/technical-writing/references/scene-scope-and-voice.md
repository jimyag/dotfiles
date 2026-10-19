# Scene, Scope, and Voice

Use this when the text is long, Chinese, requires preservation, or includes a writing sample. It combines the practical boundaries from several humanizer-style skills without turning this skill into a full writing system.

## Contents

- Protected Spans
- Scene Detection
- Edit Scope
- Voice Calibration
- Personality Boundaries

## Protected Spans

Mark these before rewriting:

- Direct quotes and attributed text.
- Code blocks, commands, logs, URLs, file paths, config keys, API names, identifiers.
- Required domain terms, product names, version names, legal/policy wording.
- Citations, footnotes, reference markers, and source titles.
- User-supplied titles when the user did not ask to change titles.

Default behavior: preserve protected spans exactly. If they contain AI-writing residue, flag it instead of silently rewriting.

## Scene Detection

Pick one main scene. Mixed text should still keep one dominant register.

| Scene | Signals | Default stance |
|---|---|---|
| `chat` | short replies, comments, collaboration messages | Minimal edits. Keep natural directness. |
| `status` | progress updates, standup notes, review summaries | Keep timeline, action, result, risk. No slogans. |
| `docs` | how-to docs, technical notes, API docs, FAQs | Preserve terms and structure. Make it searchable and reproducible. |
| `public-writing` | blog posts, social posts, essays, public commentary | Standard edits. Remove performance and template structure. |
| `translation` | translated text or bilingual polishing | Preserve source structure and meaning. Do not add headings or opinions. |

## Edit Scope

Scope is separate from pass strength.

### `structural`

Use when the user asks for a rewrite, the text is short, or the whole structure is template-like.

Allowed:

- Delete empty sentences.
- Merge adjacent factual sentences.
- Move a sentence when it fixes flow.
- Rebuild a paragraph if the original is mostly filler.

### `bounded`

Use by default for long Chinese public-writing.

Allowed:

- Clean sentence-internal filler.
- Lower inflated tone.
- Suggest deleting whole empty sentences, but do not delete them silently.

Output a short "建议删除" list when whole-sentence deletion would help. Each item should say why deletion does not remove information.

### `in-place`

Use when the user asks to preserve sentence count, structure, or wording closely.

Allowed:

- Replace local phrases.
- Remove sentence-internal route markers.
- Lower tone inside the same sentence.

Forbidden:

- Delete whole sentences.
- Merge sentences.
- Reorder paragraphs.

## Voice Calibration

When the user provides writing samples, extract patterns before editing:

- Sentence length mix.
- Paragraph openings: direct conclusion, story, question, context, or observation.
- Punctuation habits.
- Preferred certainty level.
- First-person use.
- Transition style.
- Repeated terms that are real voice, not slop.

Do not copy surface tics blindly. A useful voice profile captures how the writer thinks and structures attention, not just their catchphrases.

## Personality Boundaries

Human writing does not always mean emotional writing.

Add stronger voice only for blogs, essays, personal posts, and opinion pieces. For docs, PRs, incident reports, release notes, and technical explanations, the human version is often plain, exact, and restrained.

Good places to add voice:

- A real constraint.
- A bounded opinion.
- A specific discomfort or uncertainty.
- A concrete scene or cost.

Bad places to add voice:

- Replacing facts with feelings.
- Turning documentation into confession.
- Adding first-person when the author never used it.
- Making every paragraph end with a quotable line.
