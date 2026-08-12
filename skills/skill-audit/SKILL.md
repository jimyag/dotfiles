---
name: skill-audit
description: Use this skill when auditing an Agent Skills library for specification compliance, cross-client portability, trigger overlap, progressive disclosure, bundled script safety, or eval coverage; use it to produce an evidence-backed cleanup or migration plan, not to create a new skill.
compatibility: Requires Python 3.10+ and uv for the bundled audit script. Official reference validation uses uvx and may require network access.
---

# Audit Agent Skills

Audit skill libraries against the portable Agent Skills specification while separating hard errors, intentional client extensions, maintainability issues, and unverified behavioral quality.

For creating or substantially rewriting a skill, use the current client's skill-creation guidance when available. This skill remains useful without any specific client because its audit workflow and script are self-contained.

## Standards

1. The [Agent Skills specification](https://agentskills.io/specification) is the portable baseline.
2. Client-only fields and tool assumptions are portability exceptions, even when they work locally.
3. A valid structure does not prove useful triggering, safe scripts, or better outputs.

Read [the official checklist](references/official-agent-skills-checklist.md) for a full audit. Read [the client extension policy](references/client-extension-policy.md) when skills use non-standard frontmatter, sibling `_shared` files, plugins, connectors, or client-specific tools. Use [progressive disclosure guidance](references/progressive-disclosure.md) when a main file is large.

## Audit workflow

1. Establish scope and source of truth.
   - Separate source-managed, installed, and live copies.
   - Record the specification/reference date and intended clients.
2. Inventory each skill.
   - Capture name, description, frontmatter, line count, links, scripts, references, assets, and evals.
   - Check adjacent skills and built-in client capabilities for overlap.
3. Validate portable structure.
   - Run the official validator for intended portable skills.
   - Classify client-only fields and dependencies instead of silently accepting or deleting them.
4. Inspect disclosure and packaging.
   - Keep triggers, boundaries, minimum workflow, and high-risk constraints in `SKILL.md`.
   - Move long templates, examples, command catalogs, and troubleshooting into one-level references.
   - Verify that each skill still works when installed independently; sibling `_shared` content is not portable packaging.
5. Inspect behavior quality.
   - Check positive and near-miss negative trigger cases.
   - Look for duplicated universal behavior that belongs in client/project instructions.
   - Require baseline comparisons before claiming a rewrite improves quality or cost.
6. Prioritize findings.
   - Fix broken packaging and conflicting behavior first.
   - Then remove duplicates, merge overlapping user intents, narrow descriptions, and reduce activation context.
   - Do not optimize line count alone or split a cohesive capability into competing triggers.
7. Verify source and live state separately after changes.

## Commands

Audit one skill or a directory:

```bash
uv run scripts/audit_agent_skills.py /path/to/skills --profile portable --require-evals
```

Use `--profile local` to report documented client extensions and sibling shared references without pretending they are portable. Use `--format json` for machine-readable output.

Validate a portable skill with the reference implementation:

```bash
uvx --from skills-ref agentskills validate /path/to/skill
```

## Output contract

Report:

1. scope, inventory, and source/reference versions;
2. hard specification or packaging failures;
3. intentional client-extension exceptions;
4. overlap, verbosity, trigger, script, and eval findings;
5. delete, merge, narrow, move-to-reference, or split recommendations with reasons;
6. validation evidence and explicitly unverified behavior.

Preserve verified safety behavior until an equivalent control exists. Do not make a public skill depend on a single client plugin when a connector, CLI/API fallback, or complete manual handoff can keep it portable.

## Supporting material

- [Official checklist](references/official-agent-skills-checklist.md)
- [Client extension policy](references/client-extension-policy.md)
- [Frontmatter patterns](references/frontmatter-patterns.md)
- [Progressive disclosure](references/progressive-disclosure.md)
