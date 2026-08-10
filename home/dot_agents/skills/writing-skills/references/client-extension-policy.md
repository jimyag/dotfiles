# Client extension policy

## Contents

- Why profiles are necessary
- Portable profile
- Local client profile
- Local shared references
- Migration decision
- Review rules

## Why profiles are necessary

The open Agent Skills specification defines six top-level frontmatter fields. Codex, Claude Code, and other clients may support extra fields such as invocation controls, argument hints, path filters, or tool denials. The official `agentskills validate` implementation rejects unknown top-level fields, while removing a client safety field can change behavior.

Do not describe a client-extended skill as strictly portable merely because the local client loads it successfully.

## Portable profile

Use for skills intended to work across compatible clients.

```yaml
---
name: example-skill
description: Use this skill when ...
license: MIT
compatibility: Requires git and network access.
metadata:
  example-org.version: "1.0"
allowed-tools: Bash(git:*) Read
---
```

Rules:

- Only `name`, `description`, `license`, `compatibility`, `metadata`, and experimental `allowed-tools` appear at the top level.
- `metadata` keys and values are strings.
- `allowed-tools` is one space-separated string, not a YAML list.
- All trigger information required for discovery is present in `description`.
- Official validation must pass.

## Local client profile

Use only when a client-specific capability materially changes safety or usability and no portable equivalent exists. Examples may include:

- preventing automatic model invocation for a side-effecting workflow;
- hiding a routing-only skill from user commands;
- denying dangerous tools independently of the allowlist;
- providing command argument completion;
- path-based activation.

Rules:

- Add `compatibility` naming the intended client and required behavior.
- Document each extension field and why it cannot yet move to standard fields or external client configuration.
- Keep capability and trigger conditions in the standard `description`; extension trigger fields are supplemental.
- Test the skill in every claimed client.
- Run the bundled audit with `--profile local` and treat the extension warning as an explicit exception.
- Do not trade away a verified safety guard merely to satisfy the portable validator.

## Local shared references

A source-managed local skill library may keep genuinely shared rules under a sibling `_shared/` directory when avoiding duplicated policy is more important than independent distribution.

Rules:

- Treat `../_shared/` links as local composition, not portable Agent Skills packaging.
- Keep each shared file single-purpose and referenced by a small, explicit set of skills.
- The local audit profile reports these links as informational findings; the portable profile keeps them as warnings.
- Before publishing or installing one skill independently, materialize its shared dependencies inside that skill or move truly global policy to the client configuration.
- Do not copy shared policy into several source skills without a synchronization mechanism.

## Migration decision

For each client-extended skill, choose one path:

1. Remove redundant extensions and pass the portable validator.
2. Move routing or safety policy into a client-specific configuration file while keeping `SKILL.md` portable.
3. Keep the extension temporarily, add compatibility and test evidence, and track it as a portability exception.
4. Split a portable knowledge skill from a client-specific side-effecting workflow when both are genuinely reusable units.

Avoid duplicating the same workflow into portable and local copies without an explicit synchronization mechanism.

## Review rules

- Treat specification errors as blockers for portable release.
- Treat undocumented client extensions as blockers for claims of portability.
- Treat documented, tested safety extensions as intentional exceptions, not defects.
- Revisit exceptions when the target client adds a portable or external configuration mechanism.
