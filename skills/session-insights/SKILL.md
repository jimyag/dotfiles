---
name: session-insights
description: Use this skill when the user wants an /insights-style report or analytics from local Claude Code, Codex, or other coding-agent session history, including multi-session overlap, tool and token usage, git activity, semantic facets, or report.html generation.
---

# Session Insights

Generate an `/insights`-style usage report from local coding-agent session files. The implementation lives in `scripts/session_insights.py` so this skill can be copied into arbitrary projects without requiring the `claude-code` source tree.

## Ask First

If the user did not provide both values, ask before running:

1. Platform:
   - `claude` for Claude Code sessions
   - `codex` for Codex sessions
   - another tool only after adding a parser adapter in `scripts/session_insights.py`
2. Scope:
   - `all`
   - a file or directory path
   - `recent:N`
   - `since:YYYY-MM-DD`
   - `project:TEXT`

Treat these as the skill arguments: `[platform] [scope]`.

## Run

From the skill directory:

```bash
python3 scripts/session_insights.py --platform <platform> --scope <scope>
```

Workflow diagnosis is the default. The script writes deterministic metrics plus
per-session transcript and analysis artifacts, then the agent must read those
artifacts and fill in the semantic analysis. Do not stop after the script
prints the metrics.

If invoking from a project root, use the copied skill path:

```bash
python3 .claude/skills/session-insights/scripts/session_insights.py --platform claude --scope all
```

For deterministic counters only, opt out explicitly:

```bash
python3 scripts/session_insights.py \
  --platform <platform> \
  --scope <scope> \
  --metrics-only
```

To choose the workflow artifact directory:

```bash
python3 .claude/skills/session-insights/scripts/session_insights.py \
  --platform claude \
  --scope all \
  --export-dir /tmp/session-insights/claude-all
```

This writes to `/tmp/session-insights/<timestamp>/` by default. Use `--export-dir <dir>` to choose a directory, and `--export-limit N` to cap exported sessions.

## Current Adapters

- `claude`: scans `$CLAUDE_CONFIG_DIR/projects/*/*.jsonl` or `~/.claude/projects/*/*.jsonl`; rebuilds `uuid`/`parentUuid` conversation branches; removes `/insights` meta-sessions; deduplicates branch sessions by user-message count and duration.
- `codex`: scans `$CODEX_HOME/sessions/.../rollout-*.jsonl`, `$CODEX_HOME/archived_sessions/rollout-*.jsonl`, or `~/.codex/...`; maps Codex JSONL into the same aggregate schema. Metrics are basic because Codex event schemas differ from Claude Code.

## Output

The script prints a Markdown report and writes:

`<tool-home>/usage-data/session-insights-data.json`

For Claude Code, `<tool-home>` is `$CLAUDE_CONFIG_DIR` or `~/.claude`.
For Codex, `<tool-home>` is `$CODEX_HOME` or `~/.codex`.

By default, workflow diagnosis also writes:

- `manifest.json`
- `session-insights-data.json`
- `analysis-instructions.md`
- `transcripts/*.md`
- `analyses/*.md`
- `workflow-summary.md`

After the agent performs semantic analysis, it must also write:

- `report.json`
- `report.html`

## Extension Contract

To add another tool, update `scripts/session_insights.py`:

1. Add the platform to `platform_home()`.
2. Add a parser that converts that tool's files into `SessionMeta`-like dictionaries.
3. Route the parser from `scan_sessions()`.
4. Keep aggregation/reporting unchanged.

Required `SessionMeta` fields:

- `session_id`
- `project_path`
- `start_time`
- `duration_minutes`
- `user_message_count`
- `assistant_message_count`
- `first_prompt`
- `source_file`
- stats from `empty_stats()`

## Semantic Facets

The script computes deterministic metrics. Facet-derived sections such as goals, outcomes, satisfaction, helpfulness, session types, friction, and successes require semantic transcript analysis.

Do not hard-code workflow categories, recommendations, or semantic scoring rules in `scripts/session_insights.py`. The script should prepare evidence; the AI agent should read the transcripts and perform the analysis.

For the default workflow diagnosis:

1. Run the script normally, optionally with `--export-dir`.
2. Read `manifest.json`, `session-insights-data.json`, and `analysis-instructions.md`.
3. For each transcript in `transcripts/*.md`, write the corresponding `analyses/*.md`.
4. After per-session analyses are written, synthesize recurring issues and recommendations into `workflow-summary.md`.
5. Write `report.json` with structured insight sections.
6. Write `report.html` as a readable local report.
7. State that semantic facets are agent-generated approximations unless produced by the official tool.

The final analysis should give the user new knowledge they can apply in later
sessions. Include:

- At a Glance: what is working, what is hindering, quick wins, ambitious workflows.
- Work themes grouped by evidence from the transcripts, not fixed categories.
- Wins and effective patterns.
- Friction points with evidence and attribution when possible.
- AGENTS.md candidates that are directly pasteable and durable.
- Skill candidates for repeated operations that deserve reusable workflows.
- Copyable prompts the user can paste into future Codex sessions.
- On-the-horizon workflows grounded in observed behavior.

For skill candidates, include the proposed skill name, trigger, why it recurs,
required evidence, core steps, validation, and non-goals. Before proposing a
skill, decide whether the repeated behavior is better represented as:

- AGENTS.md: a short durable behavior rule
- Skill: a multi-step reusable workflow with evidence and validation
- Script: deterministic local automation
- Memory/docs: project-specific facts or prior decisions
- Nothing: one-off detail that should not become durable process

If the transcript set is large, process in batches and keep notes in the
analysis files. Do not analyze only a tiny sample unless the user explicitly
requested a sample.

## Verification

Before finishing:

1. Report the platform and scope used.
2. Report `total_sessions_scanned`, `raw_deduped_sessions`, and `total_sessions`.
3. Confirm the JSON output path exists.
4. Unless `--metrics-only` was used, confirm `manifest.json`, `analysis-instructions.md`, `transcripts/`, `analyses/`, `workflow-summary.md`, `report.json`, and `report.html` exist.
5. Say which parts are deterministic metrics and which parts are approximations.
