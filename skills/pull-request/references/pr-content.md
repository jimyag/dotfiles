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
- Include real validation commands and results; write `Not verified` when unknown.
- State breaking changes, migration steps, configuration changes, compatibility limits, and reviewer focus.
- Reference a related issue, ticket, or design document when one exists.
- Show the key point with the smallest view that makes it clear: pseudocode for logic, a call tree for control flow, a component tree for UI structure, a shallow file tree for a broad refactor, Mermaid for interactions, or a `diff` sketch when the point is what changes in an existing shape. Place each visual beside the sentence it supports and keep only the calls, files and states the reviewer needs.
- Prefer before/after evidence: screenshots for visual changes, otherwise the exact failing-then-passing test or command output.
- State merge danger: whether the change is a one-way door (destructive or hard to reverse) or a two-way door (cheap to roll back), and its blast radius (who or what could break: consumers, layout, mobile, data).

When no repository template exists, use:

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

Call out one or two areas whose correctness or design deserves attention. If the diff contains unrelated concerns or is difficult to summarize coherently, say so and recommend a concrete split.
