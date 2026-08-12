---
name: gh-stack
description: Manage stacked branches and pull requests with the gh-stack GitHub CLI extension. Use when creating, pushing, rebasing, syncing, navigating, viewing, restructuring, or merging dependent PR chains and stacked diffs.
compatibility: Requires git, authenticated GitHub CLI, network access, and the github/gh-stack extension.
metadata:
  author: github
  version: "0.0.9"
---

# Manage stacked pull requests

Use `gh stack` for a linear chain of branches where each branch has one focused PR based on the branch below it.

```text
main -> data-models -> api -> frontend
```

Put foundational changes lower in the stack and dependent consumers higher. Use separate stacks for unrelated work.

## Preflight

```bash
git rev-parse --git-dir
git status --short
gh --version
gh auth status
gh extension list | rg 'github/gh-stack'
```

Install when explicitly authorized:

```bash
gh extension install github/gh-stack
```

With multiple remotes, configure the intended default or pass `--remote` where supported:

```bash
git config remote.pushDefault origin
```

## Non-interactive rules

- Always pass branch names to `init`, `add`, and branch-based `checkout`; omitted arguments can prompt.
- Always use `gh stack submit --auto`; add `--open` only for ready-for-review PRs.
- Always use `gh stack view --json`; the default view is interactive.
- Use normal `git add` and `git commit` to keep each layer deliberate.
- Before changing a lower layer, navigate down, commit there, then run `gh stack rebase --upstack`.
- A branch shared by multiple stacks requires checking out an unambiguous branch first.
- Before `checkout <pr-number>`, remove conflicting local tracking with `gh stack unstack --local` when necessary.
- Merge with `gh stack merge --yes`; do not substitute `gh pr merge` for stacked PRs.

## Common workflows

Create and submit a stack:

```bash
gh stack init data-models
# edit, git add, git commit
gh stack add api
# edit, git add, git commit
gh stack add frontend
# edit, git add, git commit
gh stack submit --auto
gh stack view --json
```

Change a lower layer and update dependents:

```bash
gh stack checkout api
# edit, git add, git commit
gh stack rebase --upstack
gh stack push
gh stack view --json
```

Routine synchronization:

```bash
gh stack sync
gh stack view --json
```

For exact flags, stack linking, restructuring, conflict recovery, merge queues, exit codes, and command-specific behavior, read [the complete command reference](references/complete-reference.md) before executing the relevant operation.

## Recovery boundaries

- Rebase conflict: resolve reported files, stage them, then `gh stack rebase --continue`; abort with `gh stack rebase --abort` if resolution is unsafe.
- Multiple-stack ambiguity: check out a specific non-shared branch; do not guess.
- GitHub API failure: inspect authentication and stderr before retrying.
- Locked stack state: confirm no active `gh stack` process before retrying.
- Repository lacks stacked-PR support: report the limitation; do not emulate it with unrelated commands.

## Verification

After every mutating workflow, run `gh stack view --json` and verify branch order, bases, PR state, and rebase status. Report commands and actual output coverage rather than claiming the whole stack is healthy from a successful push alone.
