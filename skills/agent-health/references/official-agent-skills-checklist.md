# Official Agent Skills checklist

## Contents

- Source baseline
- Portable format requirements
- Progressive disclosure and references
- Description design and trigger evaluation
- Output-quality evaluation
- Script design
- Authoring and iteration practices
- Completion checklist

## Source baseline

This checklist is derived from the Agent Skills documentation retrieved on 2026-08-07:

- [Overview](https://agentskills.io/home)
- [Specification](https://agentskills.io/specification)
- [Quickstart](https://agentskills.io/skill-creation/quickstart)
- [Best practices](https://agentskills.io/skill-creation/best-practices)
- [Optimizing descriptions](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Evaluating skills](https://agentskills.io/skill-creation/evaluating-skills)
- [Using scripts](https://agentskills.io/skill-creation/using-scripts)

Treat specification language as required. Treat creation-guide language as recommended unless it explicitly calls something a hard requirement.

## Portable format requirements

### Directory and file

- A skill is a directory containing `SKILL.md`.
- `SKILL.md` contains YAML frontmatter followed by Markdown instructions.
- Optional conventional directories are `scripts/`, `references/`, and `assets/`.

### Frontmatter

The portable top-level fields are:

| Field | Requirement |
|---|---|
| `name` | Required string, 1-64 characters, lowercase ASCII letters/numbers/single hyphens, no leading/trailing/consecutive hyphen, identical to parent directory. |
| `description` | Required non-empty string, maximum 1024 characters, describes both capability and when to use it, includes specific discovery keywords. |
| `license` | Optional short license name or bundled license-file reference. |
| `compatibility` | Optional non-empty string, maximum 500 characters, only for relevant product, package, runtime, or network requirements. |
| `metadata` | Optional map whose keys and values are strings; use reasonably unique keys. |
| `allowed-tools` | Optional experimental space-separated string; implementation support varies. |

Unknown top-level fields fail the official `agentskills validate` reference implementation. Use the client-extension policy linked directly from `SKILL.md` before adding them.

### Body

- Include the steps, examples, and edge cases that materially improve execution.
- Do not explain concepts the agent already understands.
- Prefer a reusable procedure over an answer for one specific task.
- Give a clear default when multiple approaches are possible; mention alternatives briefly.
- Match prescriptiveness to fragility: flexible heuristics for tolerant tasks, exact commands and gates for fragile tasks.

### Official validation

Run:

```bash
uvx --from skills-ref agentskills validate /path/to/skill
```

Validation proves portable structure and frontmatter only. It does not prove useful triggering, good outputs, safe scripts, or cross-model reliability.

## Progressive disclosure and references

- Startup loads only `name` and `description`; activation loads all of `SKILL.md`; supporting resources load on demand.
- Keep `SKILL.md` under 500 lines and about 5,000 tokens.
- Keep in `SKILL.md`: scope, triggers, boundaries, minimum workflow, high-risk constraints, non-obvious gotchas, and conditional links.
- Move out: long API references, example collections, setup guides, templates, detailed decision tables, troubleshooting catalogs, and reusable scripts.
- Use relative paths from the skill root.
- Keep references one directory deep from `SKILL.md`; avoid reference-to-reference chains.
- Tell the agent exactly when to load each support file.
- Give reference files longer than 100 lines a contents section so partial readers can see their scope.
- Put static templates, images, schemas, and lookup data in `assets/`.

## Description design and trigger evaluation

### Description content

- Use imperative trigger phrasing such as `Use this skill when ...`.
- Describe the user's intended outcome, not internal implementation.
- Include indirect contexts where the skill helps even if the user does not name the format or domain.
- Stay concise and below 1024 characters.
- Cover both positive scope and important adjacent boundaries without turning the description into a workflow.

### Trigger query set

- Aim for about 20 realistic queries: 8-10 positive and 8-10 negative.
- Vary phrasing, explicitness, detail, complexity, casual language, typos, paths, and contextual backstory.
- Make negative examples near-misses that share keywords but require a neighboring capability.
- Avoid irrelevant negatives that cannot test precision.

### Trigger evaluation

- Confirm the skill is registered and observe whether the client actually loads `SKILL.md`.
- Run each query multiple times; three is a reasonable starting point.
- Compute trigger rate. A suggested threshold is above 0.5 for positives and below 0.5 for negatives.
- Split queries into a fixed training set (about 60%) and validation set (about 40%) with balanced labels.
- Use only training failures to revise the description; select the best iteration by validation pass rate.
- Generalize categories instead of copying failed-query keywords.
- Five iterations are usually enough; if results plateau, revisit labels and query quality.
- After selection, run 5-10 fresh holdout queries for an honest final check.

## Output-quality evaluation

### Test cases

- Store structured cases in `evals/evals.json`.
- Each case contains a realistic prompt, human-readable expected output, and optional input files.
- Start with 2-3 cases, vary prompt style, and include at least one boundary or malformed-input case.

### Baseline and isolation

- Run every case with the skill and without it; for an existing skill, compare against a snapshot of the prior version.
- Start every run with clean context and separate output directories.
- Record duration and token count immediately for each run.

### Assertions and grading

- Add assertions after inspecting initial outputs.
- Assertions must be specific and observable without requiring brittle exact wording.
- Use code for mechanical checks and LLM judgment for semantic checks.
- Require concrete output evidence for every PASS.
- Review whether assertions are too easy, impossible, or unverifiable.
- Use blind comparison for holistic quality when comparing versions.

### Aggregation and iteration

- Aggregate pass rates, time, tokens, standard deviation when repeated runs exist, and with-skill deltas.
- Remove assertions that always pass with and without the skill.
- Investigate assertions that always fail in both configurations.
- Study where the skill uniquely helps and tighten ambiguous instructions when results vary.
- Review actual outputs with a human and record actionable feedback.
- Revise from failed assertions, human feedback, and execution traces together.
- Generalize fixes, keep the skill lean, explain why where it improves judgment, and bundle repeated helper logic.
- Repeat in a new iteration directory until feedback is consistently empty or improvement stops.

## Script design

### One-off tools

- Prefer a version-pinned one-off command when an existing tool already solves the problem.
- Recommended examples include `uvx`, `pipx`, `npx`, `bunx`, `deno run`, and `go run` according to the user's runtime.
- State prerequisites in `SKILL.md`; use `compatibility` for runtime-level requirements.
- Move a command into `scripts/` when its flags or control flow become error-prone.

### Bundled scripts

- Reference scripts with paths relative to the skill root and list their purpose in `SKILL.md`.
- Keep scripts self-contained or explicitly document dependencies.
- For Python, use PEP 723 metadata and run with `uv run`.
- Bound dependencies with PEP 508 specifiers; use `uv lock --script` when full reproducibility matters.
- Include helpful error messages and graceful edge-case handling.

### Agent-facing interface

- Non-interactive behavior is a hard requirement: accept flags, environment variables, or stdin instead of TTY prompts.
- Provide concise `--help` with arguments, defaults, and examples.
- Errors state what failed, what was expected, and what the agent should try next.
- Prefer JSON/CSV/TSV stdout; send progress and diagnostics to stderr.
- Make stateful behavior idempotent where possible.
- Reject ambiguous input rather than guessing; prefer enums and closed sets.
- Add `--dry-run` or equivalent planning for destructive/stateful operations.
- Use meaningful documented exit codes.
- Require explicit confirmation or force flags for dangerous behavior.
- Bound output size with summaries, limits, offsets, pagination, or explicit output files.

## Authoring and iteration practices

- Ground skills in real expertise: completed tasks, corrections, runbooks, specifications, schemas, review history, patches, incidents, and resolved failures.
- Read execution traces, not only final answers.
- A skill should encode one coherent capability that composes with neighboring skills.
- Add only knowledge the agent would otherwise miss.
- Prefer concise stepwise guidance and one strong example over exhaustive catalogs.
- Keep concrete gotchas close enough that the agent sees them before making the mistake.
- Use templates for required output formats.
- Use checklists for dependent multi-step workflows.
- Use validation loops: execute, validate, repair, repeat.
- For batch or destructive work, use plan-validate-execute against a source of truth.
- Bundle a tested script when traces show the agent recreating the same logic repeatedly.
- Test every model/client you intend to support; instructions may need different detail levels.

## Completion checklist

- [ ] Official validator passes for the chosen portable profile, or every client extension is documented as an intentional exception.
- [ ] Name, directory, description, metadata types, license, compatibility, and allowed-tools satisfy the selected profile.
- [ ] Description has positive and near-miss negative trigger cases.
- [ ] Scope is coherent and does not collide silently with adjacent skills.
- [ ] `SKILL.md` is within the disclosure budget or split with direct conditional references.
- [ ] Long references have contents sections and no deep reference chains.
- [ ] Scripts are non-interactive, dependency-declared, version-bounded, helpful on error, safe by default, and bounded in output.
- [ ] Output evals compare against a baseline in clean contexts with evidence-backed grading.
- [ ] Trigger rate, output-quality delta, time, and token cost are recorded or explicitly marked unverified.
- [ ] Source and installed/live copies are checked separately when configuration management is involved.
