# Progressive Disclosure

## Goal

Keep `SKILL.md` short enough that invoking it is cheap, then point to heavier files only when needed.

## What stays in `SKILL.md`

- what the skill is for
- when to use it
- when not to use it
- the minimum execution loop
- the highest-risk constraints
- links to supporting files

## What moves out

Move these into supporting files when they start to dominate the main skill:

- long API or syntax references
- large example collections
- setup guides
- templates
- detailed decision tables
- long troubleshooting sections
- reusable scripts

## Recommended structure

```text
skill-name/
  SKILL.md
  references/
    workflow.md
    examples.md
    setup.md
  scripts/
    helper.py
```

In `SKILL.md`, explicitly tell the model when to load each file:

```markdown
## Additional resources

- For setup details, see [references/setup.md](references/setup.md).
- For output examples, see [references/examples.md](references/examples.md).
- For reusable commands, use `scripts/helper.py`.
```

## Compression heuristics

- one strong example is better than five weak ones
- link to `--help` instead of documenting every flag inline
- do not repeat workflow details that already live in another referenced file
- avoid duplicating the same rule in several sections

## Smells

Your main `SKILL.md` is too heavy when:

- the overview is buried under setup details
- command examples outnumber decision rules
- the same workflow appears in multiple sections
- the file is acting like a README plus API reference plus runbook

When that happens, split the file and turn `SKILL.md` back into a router.
