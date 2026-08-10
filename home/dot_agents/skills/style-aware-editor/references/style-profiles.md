# Style Profiles

Pick the closest profile before editing. Do not force every text into a casual voice.

## Contents

- Technical tutorial
- Engineering practice note
- Academic / formal technical
- Opinion / commentary
- Incident review / postmortem
- PR / issue / changelog
- Personal blog

## Technical tutorial

Goal: help the reader perform or understand a technical task.

Keep:

- exact commands, paths, config keys, API names
- ordered steps when sequence matters
- warnings that prevent real mistakes

Cut:

- motivational openings
- broad claims about importance
- repeated "why this matters" paragraphs
- fake conclusions

Preferred style:

- direct sentences
- concrete prerequisites
- clear failure modes
- examples over slogans

Register guardrails:

- Preserve code blocks, commands, flags, file paths, package names, API names, and config keys exactly.
- Do not replace repeated technical terms with synonyms.
- Do not remove hyphens from established technical compounds.

## Engineering practice note

Goal: explain a real engineering judgment, tradeoff, or workflow.

Keep:

- constraints
- alternatives considered
- why one option is better in this context
- validation and residual risk

Cut:

- "best practice" claims without scope
- balanced-but-empty pros/cons
- architecture astronaut language

Preferred style:

- opinionated but bounded
- "this works when..." / "this fails when..."
- small concrete examples

Register guardrails:

- Keep tradeoff language when it reflects a real constraint.
- Keep hedges like "usually", "in this repo", "for this workload" when they prevent overclaiming.
- Do not turn bounded engineering judgment into universal advice.

## Academic / formal technical

Goal: preserve formal precision while removing padding and unsupported claims.

Keep:

- citations and citation placeholders
- passive voice when standard for the field
- hedges such as "suggests", "may", "observed", "under these conditions"
- domain terms, hyphenated compounds, equations, symbols, and quoted text

Cut:

- unsupported significance claims
- speculative gap-filling
- vague authority
- inflated "important contribution" language not supported by the text

Preferred style:

- restrained
- source-bound
- precise
- no invented citations

## Opinion / commentary

Goal: make a claim and explain why.

Keep:

- the author's stance
- uncertainty when real
- examples that reveal judgment

Cut:

- fake neutrality
- "both sides" padding
- generic industry framing

Preferred style:

- clear thesis
- fewer sections
- stronger verbs
- some personality, but not performance

## Incident review / postmortem

Goal: explain what happened, why, impact, and prevention.

Keep:

- timeline
- facts and evidence
- owner-neutral causal language
- concrete follow-ups

Cut:

- drama
- blame
- inflated lessons
- vague "improve monitoring" endings

Preferred style:

- precise and accountable
- short paragraphs
- action items tied to failure modes

## PR / issue / changelog

Goal: help maintainers review or act.

Keep:

- what changed
- why it changed
- how it was verified
- risk or migration notes

Cut:

- background essays
- marketing adjectives
- generic "improves robustness"
- repeated commit list

Preferred style:

- compact
- concrete
- diff-aware
- reviewer-friendly

## Personal blog

Goal: sound like a person thinking through a topic.

Keep:

- personal framing when it adds context
- specific constraints or experiences
- direct conclusions

Cut:

- corporate polish
- over-structured sections
- teaching-script phrases
- universal claims

Preferred style:

- natural rhythm
- concise explanations
- concrete examples
- personal judgment without theatrics

Register guardrails:

- Preserve first-person voice when the author is clearly recounting experience.
- Preserve rough but meaningful phrasing.
- Do not flatten quirks into corporate prose.
