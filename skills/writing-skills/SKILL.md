---
name: writing-skills
description: Use this skill when creating, auditing, or updating Agent Skills; improving SKILL.md frontmatter, descriptions, progressive disclosure, bundled scripts, or evals; checking a skill library against agentskills.io; or deciding how client-specific extensions affect portability.
compatibility: Requires Python 3.10+ and uv for the bundled audit script. Official reference validation uses uvx and may require network access.
---

# Writing and auditing Agent Skills

Create and maintain skills as small, discoverable, evidence-backed units of reusable expertise. Treat the Agent Skills specification as the portable baseline, then apply client-specific extensions deliberately.

## Standards hierarchy

1. The [Agent Skills specification](https://agentskills.io/specification) defines portable format requirements.
2. The official creation guides define recommended authoring, description, evaluation, and script practices.
3. Client-specific fields may add useful behavior, but they are portability exceptions and must not be mistaken for open-standard fields.

Read [references/official-agent-skills-checklist.md](references/official-agent-skills-checklist.md) before creating or materially revising a skill. Read [references/client-extension-policy.md](references/client-extension-policy.md) when the skill uses non-standard frontmatter or must work across multiple clients.

## Workflow

1. Establish evidence.
   - Start from a real completed task, execution trace, runbook, issue, review history, API specification, or known failure.
   - State the failure or missing capability the skill should correct.
   - Do not create a skill for behavior the agent already performs reliably without extra context.
2. Choose one coherent scope.
   - Describe the reusable user intent, not one instance's answer.
   - Check adjacent skills for overlap before adding another skill.
   - Decide whether the target is a portable skill or a documented client-specific profile.
3. Design discovery metadata.
   - Keep `name` portable and identical to the directory name.
   - Put both capability and trigger conditions in `description`; do not rely on a client-only trigger field.
   - Build positive and near-miss negative trigger queries before optimizing wording.
4. Write the minimum execution loop.
   - Keep non-obvious constraints, gotchas, safe defaults, and validation gates in `SKILL.md`.
   - Move long references, templates, setup details, and reusable code into supporting files.
   - Link every required support file directly from `SKILL.md` and say when to load it.
5. Bundle scripts only for repeated or fragile logic.
   - Give scripts non-interactive interfaces, concise `--help`, helpful errors, safe defaults, meaningful exit codes, and bounded output.
   - Prefer structured stdout and diagnostics on stderr.
   - For Python dependencies, use PEP 723 plus `uv run`; bound versions and use `uv lock --script` when exact reproducibility matters.
6. Evaluate behavior.
   - Compare with-skill against without-skill or the previous skill version in fresh contexts.
   - Grade objective assertions with concrete evidence; use human review for holistic quality.
   - Measure quality delta together with token and time cost.
   - Read execution traces and revise general causes, not individual test phrasing.
7. Validate and report.
   - Run the bundled audit and the official reference validator.
   - Separate specification errors, portability exceptions, and best-practice warnings.
   - Re-run trigger and output evals after material changes.

## Audit commands

Audit one skill or a directory of skills:

```bash
uv run scripts/audit_agent_skills.py /path/to/skills --profile portable --require-evals
```

Use `--profile local` to report client-only frontmatter as warnings rather than errors and documented `../_shared/` dependencies as informational findings. Emit machine-readable output with `--format json`.

Run the official reference validator for each skill directory:

```bash
uvx --from skills-ref agentskills validate /path/to/skill
```

The official validator is the authority for portable frontmatter. The bundled audit adds maintainability checks that the validator does not cover.

## Output contract

For an audit or migration request, produce:

1. Scope and source versions or retrieval date.
2. Hard specification failures.
3. Intentional client-extension exceptions.
4. Best-practice gaps in descriptions, disclosure, evals, and scripts.
5. A prioritized migration plan with validation evidence for each phase.
6. Explicitly unverified behavior, especially trigger rates and output-quality deltas.

Do not bulk-remove safety fields such as auto-invocation guards merely to make a validator green. Preserve their behavior until an equivalent client-specific control exists elsewhere.

## Supporting material

- [references/official-agent-skills-checklist.md](references/official-agent-skills-checklist.md): complete portable format and authoring checklist.
- [references/client-extension-policy.md](references/client-extension-policy.md): strict portability versus local client behavior.
- [references/frontmatter-patterns.md](references/frontmatter-patterns.md): concise frontmatter patterns for both profiles.
- [references/progressive-disclosure.md](references/progressive-disclosure.md): content placement and splitting heuristics.
- [Anthropic skill authoring best practices](https://docs.anthropic.com/en/docs/agents-and-tools/agent-skills/best-practices): Claude-specific authoring guidance; consult the current official documentation only when targeting Claude clients.
