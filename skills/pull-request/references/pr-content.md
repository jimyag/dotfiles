# PR content rules

## Contents

- Evidence
- Title and language
- Body
- Template discovery
- Review focus

## Evidence

Draft from the actual base/head, commits, complete diff, validation results, repository template, and linked issue or design context. Unknown validation stays explicitly unverified.

## Title and language

- State the core behavior change; avoid generic titles such as `update`, `fix bug`, `changes`, or `WIP`.
- Follow Conventional Commits only when the repository clearly uses it.
- Preserve readability when including an issue identifier.
- Choose language from explicit user direction, existing PR/template language, related commits, then repository convention.

## Body

- Explain the problem and resulting behavior rather than copying the commit list.
- Separate core logic from generated or mechanical changes.
- Include relevant validation commands and results, or link an existing verification report or comment. Mention an unverified condition only when it affects confidence in this change; do not list unrelated deployments or checks the task did not require.
- State breaking changes, migration steps, configuration changes, compatibility limits, and reviewer focus when they apply.
- Reference a related issue, ticket, or design document when one exists.
- When prose cannot explain the key relationship clearly, show the smallest useful view: pseudocode, a call tree, Mermaid, or a `diff` sketch. Keep only the calls, files and states the reviewer needs.
- Prefer before/after evidence: screenshots for visual changes, otherwise the exact failing-then-passing test or command output.
- Explain material merge risks, affected consumers, and recovery constraints when they exist.

When no repository template exists, scale the body to the change. A simple change can use one or two paragraphs plus relevant validation; use the following headings only when they improve readability, and omit empty or repetitive sections:

```markdown
## Summary

<problem and resulting change>

## Changes

- <important change>

## Verification

- <command and result, or Not verified>

## Notes

- <risk, compatibility, migration, or reviewer focus; omit when empty>
```

## Template discovery

Search common locations without assuming one filename:

```bash
rg --files . .github 2>/dev/null | rg -i 'pull_request_template'
```

Preserve the selected template's headings, comments, and required fields. Do not replace it with the default structure merely for prettier wording.

## Review focus

Call out areas whose correctness or design needs particular attention, if any. If the diff contains unrelated concerns or is difficult to summarize coherently, say so and recommend a concrete split.
