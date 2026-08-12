---
name: pull-request
description: Use this skill when creating a GitHub pull request, updating an existing PR title or body, filling a repository PR template, or preparing complete PR content for manual publication. It works across clients by using an available GitHub connector first, falling back to gh CLI, or producing an executable handoff when neither is available.
compatibility: Requires git. Remote creation or updates require network access plus an available GitHub connector or authenticated gh CLI.
---

# Create or update a pull request

Build an accurate, reviewable PR from the real branch, diff, commits, validation results, linked work, and repository template. Do not require a particular AI client or plugin.

## Capability routing

Inspect the tools available in the current client instead of assuming a backend:

1. Use an available GitHub connector when it supports the required read or write operation.
2. Otherwise use authenticated `gh` CLI.
3. If neither can perform the remote write, generate the complete title, body, base/head information, and exact manual next step. Do not claim the PR was changed.

The fallback is a capability decision, not a reason to weaken content checks. Never ask the user to install a particular plugin merely to use this skill.

## Scope

Use for:

- creating a normal or draft PR;
- updating an existing PR title or body;
- filling or repairing a repository PR template;
- producing publication-ready PR content when remote writes are unavailable.

Do not use for commit creation, code review, CI repair, or implementation changes.

## Evidence collection

Always inspect the local repository first:

```bash
git rev-parse --git-dir
git status --short
git branch --show-current
git remote -v
git log --oneline -10
```

Then use the selected GitHub capability to determine whether the current branch already has a PR and to read its number, URL, base, head, title, body, and state. If remote metadata is unavailable, report that limitation and infer nothing that affects publication.

Determine the base branch from the existing PR, explicit user input, or the target repository's default branch. Do not hard-code `main`. Fetch the chosen base when possible, then inspect:

```bash
git log <base-remote>/<base-branch>..HEAD --oneline --no-decorate
git diff <base-remote>/<base-branch>...HEAD --stat
git diff <base-remote>/<base-branch>...HEAD
```

Read [PR content rules](references/pr-content.md) before drafting or changing title/body.

## Workflow

### Create

1. Confirm there is meaningful committed diff and identify base/head.
2. If a PR already exists for the head branch, return it instead of creating a duplicate.
3. Build title and body from evidence and preserve the repository template.
4. Push the branch only when the user requested PR creation and the branch is not remotely available.
5. Create the PR through the selected capability. Use draft only when the user requests it or the change is explicitly not ready for review.
6. Read the created PR back and verify number, URL, base, head, title, body, and draft state.

### Update

1. Read the existing PR and current diff; do not rewrite from stale local assumptions.
2. Preserve still-valid context, template sections, issue links, migration notes, and reviewer guidance.
3. Change only the requested or demonstrably stale content.
4. Update through the selected capability, then read the PR back and verify the final title/body.

### No remote write capability

Return:

- resolved or explicitly unverified base/head;
- final title;
- complete body, not a summary;
- whether a template was used;
- an exact `gh pr create` or `gh pr edit` command when `gh` is a viable manual option, otherwise a concise GitHub UI handoff;
- `Remote update: not performed`.

## Safety and accuracy

- Do not fabricate tests, issue links, migration status, reviewers, or deployment results.
- Do not hide breaking changes, configuration changes, known risks, or unrelated diff.
- Do not create a duplicate PR or silently change its base.
- Do not use PR wording to conceal an oversized or incoherent change; recommend splitting when reviewability is materially impaired.
- A generated title/body is not proof of a remote update. Report the actual backend used and the read-back result.

## Output

```text
Action: created / updated / prepared only
PR: #<number> <url> / not created
Base: <base>
Head: <head>
Backend: connector / gh / none
Template: used / not found
Verification: <read-back result or limitation>
```
