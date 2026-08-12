---
name: simplify
description: Use this skill when recently written or modified code should be simplified for clarity, consistency, and maintainability without changing behavior. Focus on recently changed code unless a broader review is explicitly requested.
license: Apache-2.0 (see LICENSE)
---

# Simplify Code

Simplify and refine code while preserving its exact functionality. Prioritize readable, explicit code over compact or clever solutions.

## Principles

1. **Preserve functionality**
   - Never change features, outputs, side effects, or externally visible behavior.
   - Treat behavior changes as out of scope unless the user explicitly requests them.

2. **Apply project standards**
   - Read and follow the repository's applicable instruction files, such as `AGENTS.md` or `CLAUDE.md`.
   - Prefer established project conventions over the generic defaults below.
   - When applicable, use consistent imports, explicit top-level return types, clear component props, established error-handling patterns, and consistent naming.

3. **Enhance clarity**
   - Reduce unnecessary complexity and nesting.
   - Eliminate redundant code and abstractions.
   - Improve readability with clear variable and function names.
   - Consolidate closely related logic without combining separate concerns.
   - Remove comments that only restate obvious code.
   - Avoid nested ternary expressions; use `if`/`else` chains or `switch` statements for multiple conditions.
   - Choose clarity over brevity.

4. **Avoid over-simplification**
   - Do not remove useful abstractions that improve organization.
   - Do not create dense one-liners or clever constructs that are harder to debug.
   - Do not combine too many concerns into one function or component.
   - Do not prioritize fewer lines over maintainability.

5. **Keep the scope narrow**
   - Refine only code modified in the current task or session unless the user explicitly requests broader cleanup.
   - Preserve unrelated user changes in the working tree.

## Workflow

1. Identify the recently modified code and its existing behavior.
2. Read the applicable project instructions and nearby conventions.
3. Find concrete opportunities to reduce complexity or improve readability.
4. Apply the smallest behavior-preserving refinements.
5. Review the diff for unintended semantic changes or scope expansion.
6. Run validation proportional to the change and allowed by the project instructions.
7. Report only significant refinements and any verification gaps.

## Source

Adapted from Anthropic's [`code-simplifier`](https://github.com/anthropics/claude-plugins-official/tree/main/plugins/code-simplifier) agent, licensed under the Apache License 2.0. Changes include conversion to the portable Agent Skills format, removal of the Claude-specific model selection, and generalization of project instruction handling.
