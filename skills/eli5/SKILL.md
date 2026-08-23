---
name: eli5
description: Explain a topic like I'm a 5 year old. Use when the user types /eli5 followed by a topic or asks for a dead-simple picture explainer of how something works.
license: Apache-2.0
---

# ELI5

Explain the topic from the current user request for someone who knows nothing about it. By default, produce a self-contained HTML visual explainer with big pictures and very few words.

Do not rely on client-specific argument placeholders such as `$ARGUMENTS`. If the user requests another format, preserve the same simple, visual-first teaching style in that format.

## Source

Adapted for cross-client Agent Skills portability from Anthropic's `claude-plugins-community/eli5` at commit `f4c9452f5ca091f1be7064d9faab1b001ea21645`. The upstream skill was authored by Thariq Shihipar. This version removes the Claude-specific `$ARGUMENTS` dependency.
