# Frontmatter patterns

## Portable default

Start with the smallest official field set:

```yaml
---
name: skill-name
description: Use this skill when [user intent, trigger conditions, and important near-miss boundary].
---
```

Add official optional fields only when they carry useful information:

- `license`: short SPDX-style name or bundled license reference.
- `compatibility`: product, runtime, system package, or network requirements.
- `metadata`: namespaced string-to-string properties.
- `allowed-tools`: experimental space-separated string; confirm client support.

The open specification does not define `when_to_use`, `argument-hint`, `disable-model-invocation`, `user-invocable`, `disallowed-tools`, `paths`, `context`, or `agent` as portable top-level fields.

## Description rules

Treat `description` as routing metadata, not a human summary:

- Start with imperative trigger language such as `Use this skill when ...`.
- Describe the user's desired outcome and recognizable contexts.
- Include the capability and when it applies.
- Cover indirect phrasing without copying individual eval queries.
- Clarify important boundaries with adjacent skills.
- Keep workflow details in the body.
- Stay below 1024 characters.

## Client-specific extensions

If local behavior depends on an extension field:

1. Read the client-extension policy linked directly from `SKILL.md`.
2. Keep the full discovery trigger in `description`.
3. Add `compatibility` for the intended client.
4. Document and test the exception.
5. Do not claim strict Agent Skills portability while the official validator rejects it.
