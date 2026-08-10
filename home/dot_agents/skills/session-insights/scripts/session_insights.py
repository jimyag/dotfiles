#!/usr/bin/env python3
"""Generate /insights-style reports from coding-agent session JSONL files."""

from __future__ import annotations

import argparse
import difflib
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


EXTENSION_TO_LANGUAGE = {
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".py": "Python",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".java": "Java",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".sh": "Shell",
    ".css": "CSS",
    ".html": "HTML",
}

AGENT_TOOL_NAMES = {"Task", "Agent"}


def parse_ts(value: Any) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except Exception:
        return None


def iso(dt: datetime | None) -> str:
    if not dt:
        return ""
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except Exception:
                    continue
                if isinstance(row, dict):
                    rows.append(row)
    except Exception:
        return []
    return rows


def msg_content(msg: dict[str, Any]) -> Any:
    message = msg.get("message") or {}
    if isinstance(message, dict):
        return message.get("content", "")
    return ""


def text_blocks(content: Any):
    if isinstance(content, str):
        if content.strip():
            yield content
    elif isinstance(content, list):
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                text = block.get("text", "")
                if isinstance(text, str) and text.strip():
                    yield text


def codex_text_blocks(content: Any):
    if isinstance(content, str):
        if content.strip():
            yield content
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") in {"input_text", "output_text", "text"}:
                text = block.get("text", "")
                if isinstance(text, str) and text.strip():
                    yield text


def codex_first_text(content: Any) -> str:
    return next((text.strip() for text in codex_text_blocks(content)), "")


def codex_tool_name(payload: dict[str, Any]) -> str:
    name = payload.get("name")
    if name:
        return str(name)
    typ = str(payload.get("type") or "")
    if typ.endswith("_call"):
        return typ.removesuffix("_call")
    return typ or "?"


def codex_tool_args(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("arguments") or payload.get("input") or {}
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except Exception:
            return {}
        return parsed if isinstance(parsed, dict) else {}
    return {}


def codex_patch_stats(text: str) -> tuple[set[str], int, int]:
    files = set()
    added = removed = 0
    for line in text.splitlines():
        for prefix in ("*** Add File: ", "*** Update File: ", "*** Delete File: "):
            if line.startswith(prefix):
                files.add(line.removeprefix(prefix).strip())
                break
        if line.startswith("+") and not line.startswith("+++"):
            added += 1
        elif line.startswith("-") and not line.startswith("---"):
            removed += 1
    return files, added, removed


def codex_patch_text(payload: dict[str, Any]) -> str:
    raw = payload.get("input") or payload.get("arguments") or ""
    if isinstance(raw, str):
        if raw.lstrip().startswith("*** Begin Patch"):
            return raw
        try:
            parsed = json.loads(raw)
        except Exception:
            return ""
        if isinstance(parsed, dict):
            for key in ("patch", "input", "text"):
                value = parsed.get(key)
                if isinstance(value, str) and value.lstrip().startswith("*** Begin Patch"):
                    return value
    elif isinstance(raw, dict):
        for key in ("patch", "input", "text"):
            value = raw.get(key)
            if isinstance(value, str) and value.lstrip().startswith("*** Begin Patch"):
                return value
    return ""


def codex_output_metadata(payload: dict[str, Any]) -> dict[str, Any]:
    output = payload.get("output")
    if isinstance(output, dict):
        metadata = output.get("metadata") or {}
        return metadata if isinstance(metadata, dict) else {}
    if isinstance(output, str):
        try:
            parsed = json.loads(output)
        except Exception:
            return {}
        if isinstance(parsed, dict):
            metadata = parsed.get("metadata") or {}
            return metadata if isinstance(metadata, dict) else {}
    return {}


def is_codex_internal_user_text(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("# AGENTS.md instructions") or stripped.startswith("<skill>")


def user_has_text(msg: dict[str, Any]) -> bool:
    if msg.get("type") != "user" or not msg.get("message"):
        return False
    return any(True for _ in text_blocks(msg_content(msg)))


def first_prompt(chain: list[dict[str, Any]]) -> str:
    for msg in chain:
        if msg.get("type") == "user":
            for text in text_blocks(msg_content(msg)):
                if text.strip():
                    return text.strip()
    return ""


def project_from_path(path: Path) -> str:
    return path.parent.name or "unknown"


def session_id_for(path: Path, rows: list[dict[str, Any]], chain: list[dict[str, Any]]) -> str:
    for msg in reversed(chain or rows):
        sid = msg.get("sessionId") or msg.get("session_id")
        if sid:
            return str(sid)
    return path.stem


def build_claude_chains(rows: list[dict[str, Any]]) -> list[list[dict[str, Any]]]:
    with_uuid = [r for r in rows if r.get("uuid")]
    if not with_uuid:
        return [rows] if rows else []

    by_uuid = {r.get("uuid"): r for r in with_uuid}
    children: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for row in with_uuid:
        parent = row.get("parentUuid")
        if parent and parent in by_uuid:
            children[parent].append(row)

    leaves = [row for row in with_uuid if row.get("uuid") not in children]
    if not leaves:
        leaves = [with_uuid[-1]]

    def key(row: dict[str, Any]) -> str:
        return str(row.get("timestamp", ""))

    for vals in children.values():
        vals.sort(key=key)
    leaves.sort(key=key)

    chains: list[list[dict[str, Any]]] = []
    for leaf in leaves:
        chain = []
        cur = leaf
        seen = set()
        while cur and cur.get("uuid") not in seen:
            seen.add(cur.get("uuid"))
            chain.append(cur)
            parent = cur.get("parentUuid")
            cur = by_uuid.get(parent) if parent else None
        chain.reverse()
        if chain:
            chains.append(chain)
    return chains


def categorize_tool_error(content: Any) -> str:
    text = content if isinstance(content, str) else json.dumps(content, ensure_ascii=False)
    lower = text.lower()
    if "exit code" in lower:
        return "Command Failed"
    if "rejected" in lower or "doesn't want" in lower:
        return "User Rejected"
    if "string to replace not found" in lower or "no changes" in lower:
        return "Edit Failed"
    if "modified since read" in lower:
        return "File Changed"
    if "exceeds maximum" in lower or "too large" in lower:
        return "File Too Large"
    if "file not found" in lower or "does not exist" in lower:
        return "File Not Found"
    return "Other"


def line_delta(old: str, new: str) -> tuple[int, int]:
    old_lines = old.splitlines()
    new_lines = new.splitlines()
    added = removed = 0
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=old_lines, b=new_lines).get_opcodes():
        if tag in ("replace", "delete"):
            removed += i2 - i1
        if tag in ("replace", "insert"):
            added += j2 - j1
    return added, removed


def empty_stats() -> dict[str, Any]:
    return {
        "tool_counts": {},
        "languages": {},
        "git_commits": 0,
        "git_pushes": 0,
        "input_tokens": 0,
        "output_tokens": 0,
        "user_interruptions": 0,
        "user_response_times": [],
        "tool_errors": 0,
        "tool_error_categories": {},
        "uses_task_agent": False,
        "uses_mcp": False,
        "uses_web_search": False,
        "uses_web_fetch": False,
        "lines_added": 0,
        "lines_removed": 0,
        "files_modified": 0,
        "message_hours": [],
        "user_message_timestamps": [],
    }


def extract_claude_stats(chain: list[dict[str, Any]]) -> dict[str, Any]:
    stats = empty_stats()
    tool_counts = Counter()
    languages = Counter()
    files_modified = set()
    tool_error_categories = Counter()
    last_assistant_ts = None

    for msg in chain:
        ts = msg.get("timestamp")
        dt = parse_ts(ts)

        if msg.get("type") == "assistant" and msg.get("message"):
            if dt:
                last_assistant_ts = ts
            message = msg.get("message") or {}
            usage = message.get("usage") or {}
            stats["input_tokens"] += int(usage.get("input_tokens") or 0)
            stats["output_tokens"] += int(usage.get("output_tokens") or 0)

            content = msg_content(msg)
            if isinstance(content, list):
                for block in content:
                    if not isinstance(block, dict) or block.get("type") != "tool_use":
                        continue
                    name = str(block.get("name") or "?")
                    tool_counts[name] += 1
                    stats["uses_task_agent"] = stats["uses_task_agent"] or name in AGENT_TOOL_NAMES
                    stats["uses_mcp"] = stats["uses_mcp"] or name.startswith("mcp__")
                    stats["uses_web_search"] = stats["uses_web_search"] or name == "WebSearch"
                    stats["uses_web_fetch"] = stats["uses_web_fetch"] or name == "WebFetch"

                    inp = block.get("input") or {}
                    if not isinstance(inp, dict):
                        continue
                    file_path = str(inp.get("file_path") or "")
                    if file_path:
                        lang = EXTENSION_TO_LANGUAGE.get(Path(file_path).suffix)
                        if lang:
                            languages[lang] += 1
                        if name in {"Edit", "Write"}:
                            files_modified.add(file_path)
                    if name == "Edit":
                        added, removed = line_delta(str(inp.get("old_string") or ""), str(inp.get("new_string") or ""))
                        stats["lines_added"] += added
                        stats["lines_removed"] += removed
                    if name == "Write":
                        content_text = str(inp.get("content") or "")
                        if content_text:
                            stats["lines_added"] += content_text.count("\n") + 1
                    command = str(inp.get("command") or "")
                    if "git commit" in command:
                        stats["git_commits"] += 1
                    if "git push" in command:
                        stats["git_pushes"] += 1

        if msg.get("type") == "user" and msg.get("message"):
            content = msg_content(msg)
            if user_has_text(msg) and dt:
                stats["message_hours"].append(dt.astimezone().hour)
                stats["user_message_timestamps"].append(iso(dt))
                prev = parse_ts(last_assistant_ts)
                if prev:
                    delta = (dt - prev).total_seconds()
                    if 2 < delta < 3600:
                        stats["user_response_times"].append(delta)

            for text in text_blocks(content):
                if "[Request interrupted by user" in text:
                    stats["user_interruptions"] += 1
                    break

            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result" and block.get("is_error"):
                        stats["tool_errors"] += 1
                        tool_error_categories[categorize_tool_error(block.get("content", ""))] += 1

    stats["tool_counts"] = dict(tool_counts)
    stats["languages"] = dict(languages)
    stats["tool_error_categories"] = dict(tool_error_categories)
    stats["files_modified"] = len(files_modified)
    return stats


def is_claude_meta_session(chain: list[dict[str, Any]]) -> bool:
    for msg in chain[:5]:
        if msg.get("type") == "user":
            for text in text_blocks(msg_content(msg)):
                if "RESPOND WITH ONLY A VALID JSON OBJECT" in text or "record_facets" in text:
                    return True
    return False


def claude_chain_meta(path: Path, rows: list[dict[str, Any]], chain: list[dict[str, Any]]) -> dict[str, Any] | None:
    timestamps = [parse_ts(m.get("timestamp")) for m in chain]
    timestamps = [t for t in timestamps if t]
    if not timestamps:
        return None
    start, end = min(timestamps), max(timestamps)
    stats = extract_claude_stats(chain)
    meta = {
        "session_id": session_id_for(path, rows, chain),
        "project_path": next((m.get("cwd") for m in chain if m.get("cwd")), project_from_path(path)),
        "start_time": iso(start),
        "duration_minutes": round(max(0, (end - start).total_seconds() / 60)),
        "user_message_count": sum(1 for m in chain if user_has_text(m)),
        "assistant_message_count": sum(1 for m in chain if m.get("type") == "assistant"),
        "first_prompt": first_prompt(chain)[:500],
        "source_file": str(path),
    }
    meta.update(stats)
    return meta


def codex_meta(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any] | None:
    stats = empty_stats()
    tool_counts = Counter()
    languages = Counter()
    tool_error_categories = Counter()
    files_modified = set()
    session_id = path.stem.replace("rollout-", "")
    project_path = "unknown"
    cli_version = ""
    user_count = 0
    assistant_count = 0
    first = ""
    timestamps = []
    last_assistant_ts = None
    seen_user_texts = set()

    for row in rows:
        typ = row.get("type")
        payload = row.get("payload") or {}
        ts = payload.get("timestamp") or row.get("timestamp")
        dt = parse_ts(ts)
        if dt:
            timestamps.append(dt)
        if typ == "session_meta":
            session_id = str(payload.get("id") or session_id)
            project_path = str(payload.get("cwd") or project_path)
            cli_version = str(payload.get("cli_version") or cli_version)
        elif typ == "turn_context":
            project_path = str(payload.get("cwd") or project_path)
        elif typ == "event_msg":
            event_type = payload.get("type")
            if event_type == "user_message":
                text = str(payload.get("message") or "").strip()
                if not text or is_codex_internal_user_text(text) or text in seen_user_texts:
                    continue
                seen_user_texts.add(text)
                user_count += 1
                if not first:
                    first = text
                if dt:
                    stats["message_hours"].append(dt.astimezone().hour)
                    stats["user_message_timestamps"].append(iso(dt))
                    prev = parse_ts(last_assistant_ts)
                    if prev:
                        delta = (dt - prev).total_seconds()
                        if 2 < delta < 3600:
                            stats["user_response_times"].append(delta)
                if "[Request interrupted by user" in text:
                    stats["user_interruptions"] += 1
            elif event_type == "turn_aborted":
                stats["user_interruptions"] += 1
            elif event_type == "exec_command_end":
                cmd = payload.get("command") or []
                command = " ".join(str(part) for part in cmd) if isinstance(cmd, list) else str(cmd)
                if "git commit" in command:
                    stats["git_commits"] += 1
                if "git push" in command:
                    stats["git_pushes"] += 1
                parsed_cmds = payload.get("parsed_cmd") or []
                if isinstance(parsed_cmds, list):
                    for parsed in parsed_cmds:
                        if not isinstance(parsed, dict):
                            continue
                        file_path = str(parsed.get("path") or "")
                        if file_path:
                            lang = EXTENSION_TO_LANGUAGE.get(Path(file_path).suffix)
                            if lang:
                                languages[lang] += 1
                        if parsed.get("type") in {"write", "edit"} and file_path:
                            files_modified.add(file_path)
                exit_code = payload.get("exit_code")
                if exit_code is None:
                    metadata = payload.get("metadata") or {}
                    if isinstance(metadata, dict):
                        exit_code = metadata.get("exit_code")
                if exit_code not in (None, 0, "0"):
                    stats["tool_errors"] += 1
                    tool_error_categories["Command Failed"] += 1
        elif typ == "response_item":
            item_type = payload.get("type")
            role = payload.get("role")
            if item_type == "message" and role == "user":
                text = codex_first_text(payload.get("content"))
                if text and not is_codex_internal_user_text(text) and text not in seen_user_texts:
                    seen_user_texts.add(text)
                    user_count += 1
                    if not first:
                        first = text
                    if dt:
                        stats["message_hours"].append(dt.astimezone().hour)
                        stats["user_message_timestamps"].append(iso(dt))
                        prev = parse_ts(last_assistant_ts)
                        if prev:
                            delta = (dt - prev).total_seconds()
                            if 2 < delta < 3600:
                                stats["user_response_times"].append(delta)
                    if "[Request interrupted by user" in text:
                        stats["user_interruptions"] += 1
            elif item_type == "message" and role == "assistant":
                assistant_count += 1
                if dt:
                    last_assistant_ts = ts
                usage = payload.get("usage") or {}
                if isinstance(usage, dict):
                    stats["input_tokens"] += int(usage.get("input_tokens") or 0)
                    stats["output_tokens"] += int(usage.get("output_tokens") or 0)
            elif item_type in {"function_call", "custom_tool_call", "web_search_call", "tool_search_call"}:
                name = codex_tool_name(payload)
                tool_counts[name] += 1
                stats["uses_task_agent"] = stats["uses_task_agent"] or name in AGENT_TOOL_NAMES
                stats["uses_mcp"] = stats["uses_mcp"] or name.startswith("mcp__")
                stats["uses_web_search"] = stats["uses_web_search"] or item_type == "web_search_call" or name == "web_search"
                stats["uses_web_fetch"] = stats["uses_web_fetch"] or name in {"web_fetch", "WebFetch"}
                args = codex_tool_args(payload)
                file_path = str(args.get("file_path") or args.get("path") or "")
                if file_path:
                    lang = EXTENSION_TO_LANGUAGE.get(Path(file_path).suffix)
                    if lang:
                        languages[lang] += 1
                    if name in {"apply_patch", "write", "edit", "Write", "Edit"}:
                        files_modified.add(file_path)
                command = str(args.get("command") or args.get("cmd") or "")
                if "git commit" in command:
                    stats["git_commits"] += 1
                if "git push" in command:
                    stats["git_pushes"] += 1
                if name == "apply_patch":
                    patch = codex_patch_text(payload)
                    patch_files, added, removed = codex_patch_stats(patch)
                    files_modified.update(patch_files)
                    stats["lines_added"] += added
                    stats["lines_removed"] += removed
                    for patch_file in patch_files:
                        lang = EXTENSION_TO_LANGUAGE.get(Path(patch_file).suffix)
                        if lang:
                            languages[lang] += 1
            elif item_type in {"function_call_output", "custom_tool_call_output", "tool_search_output"}:
                metadata = codex_output_metadata(payload)
                exit_code = metadata.get("exit_code")
                if exit_code not in (None, 0, "0"):
                    stats["tool_errors"] += 1
                    tool_error_categories["Command Failed"] += 1

    if not timestamps:
        return None
    start, end = min(timestamps), max(timestamps)
    meta = {
        "session_id": session_id,
        "project_path": project_path,
        "start_time": iso(start),
        "duration_minutes": round(max(0, (end - start).total_seconds() / 60)),
        "user_message_count": user_count,
        "assistant_message_count": assistant_count,
        "first_prompt": first[:500],
        "source_file": str(path),
        "cli_version": cli_version,
    }
    stats["tool_counts"] = dict(tool_counts)
    stats["languages"] = dict(languages)
    stats["tool_error_categories"] = dict(tool_error_categories)
    stats["files_modified"] = len(files_modified)
    meta.update(stats)
    return meta


def platform_home(platform: str) -> tuple[Path, Path, list[str]]:
    if platform == "claude":
        home = Path(os.environ.get("CLAUDE_CONFIG_DIR") or Path.home() / ".claude").expanduser()
        return home, home / "projects", ["*/*.jsonl"]
    if platform == "codex":
        home = Path(os.environ.get("CODEX_HOME") or Path.home() / ".codex").expanduser()
        return home, home, ["sessions/*/*/*/rollout-*.jsonl", "archived_sessions/rollout-*.jsonl"]
    raise SystemExit(f"Unsupported platform adapter: {platform}")


def files_for_scope(platform: str, scope: str) -> tuple[Path, list[Path]]:
    home, default_root, patterns = platform_home(platform)
    scope = scope or "all"
    path_scope = Path(scope).expanduser()
    project_filter = None
    recent_limit = None

    if scope.startswith("recent:"):
        recent_limit = int(scope.split(":", 1)[1])
        roots = [default_root]
    elif scope.startswith("since:"):
        roots = [default_root]
    elif scope.startswith("project:"):
        project_filter = scope.split(":", 1)[1].lower()
        roots = [default_root]
    elif scope == "all":
        roots = [default_root]
    elif path_scope.is_file():
        return home, [path_scope]
    elif path_scope.is_dir():
        roots = [path_scope]
        patterns = ["**/*.jsonl"]
    else:
        raise SystemExit(f"Scope not found or unsupported: {scope}")

    files: list[Path] = []
    for root in roots:
        for pattern in patterns:
            files.extend(root.glob(pattern))
    files = [p for p in files if p.is_file()]
    if project_filter:
        files = [p for p in files if project_filter in str(p).lower()]
    files = sorted(set(files), key=lambda p: p.stat().st_mtime, reverse=True)
    if recent_limit is not None:
        files = files[:recent_limit]
    return home, files


def scope_since_datetime(scope: str) -> datetime | None:
    if not scope.startswith("since:"):
        return None
    return parse_ts(scope.split(":", 1)[1] + "T00:00:00Z")


def dedupe_sessions(metas: list[dict[str, Any]]) -> list[dict[str, Any]]:
    best: dict[str, dict[str, Any]] = {}
    for meta in metas:
        sid = meta["session_id"]
        old = best.get(sid)
        if (
            old is None
            or meta["user_message_count"] > old["user_message_count"]
            or (
                meta["user_message_count"] == old["user_message_count"]
                and meta["duration_minutes"] > old["duration_minutes"]
            )
        ):
            best[sid] = meta
    return sorted(best.values(), key=lambda m: m["start_time"], reverse=True)


def scan_sessions(platform: str, scope: str) -> tuple[Path, int, list[dict[str, Any]]]:
    home, files = files_for_scope(platform, scope)
    since_dt = scope_since_datetime(scope)
    metas: list[dict[str, Any]] = []

    for path in files:
        rows = read_jsonl(path)
        if platform == "claude":
            for chain in build_claude_chains(rows):
                if is_claude_meta_session(chain):
                    continue
                meta = claude_chain_meta(path, rows, chain)
                if meta:
                    metas.append(meta)
        elif platform == "codex":
            meta = codex_meta(path, rows)
            if meta:
                metas.append(meta)

    if since_dt:
        metas = [m for m in metas if (parse_ts(m.get("start_time")) or datetime.min.replace(tzinfo=timezone.utc)) >= since_dt]

    return home, len(files), dedupe_sessions(metas)


def median(values: list[float]) -> float:
    if not values:
        return 0
    vals = sorted(values)
    mid = len(vals) // 2
    if len(vals) % 2:
        return vals[mid]
    return (vals[mid - 1] + vals[mid]) / 2


def multi_session_overlap(sessions: list[dict[str, Any]]) -> dict[str, int]:
    flat = []
    for session in sessions:
        for ts in session.get("user_message_timestamps", []):
            dt = parse_ts(ts)
            if dt:
                flat.append((dt.timestamp() * 1000, session["session_id"]))
    flat.sort()
    window_ms = 30 * 60 * 1000
    overlaps = 0
    involved = set()
    last = {}
    wl = 0
    for i, (ti, sid) in enumerate(flat):
        while wl < i and ti - flat[wl][0] > window_ms:
            old_sid = flat[wl][1]
            if last.get(old_sid) == wl:
                del last[old_sid]
            wl += 1
        prev = last.get(sid)
        if prev is not None:
            for j in range(prev + 1, i):
                if flat[j][1] != sid:
                    overlaps += 1
                    involved.add(sid)
                    involved.add(flat[j][1])
                    break
        last[sid] = i
    return {"overlap_events": overlaps, "sessions_involved": len(involved), "user_messages_during": overlaps}


def aggregate(platform: str, scope: str, scanned: int, sessions: list[dict[str, Any]]) -> dict[str, Any]:
    substantive = [s for s in sessions if s["user_message_count"] >= 2 and s["duration_minutes"] >= 1]
    counters = {
        "tool_counts": Counter(),
        "languages": Counter(),
        "projects": Counter(),
        "tool_error_categories": Counter(),
    }
    dates = []
    response_times = []
    hours = []
    totals = Counter()
    for session in substantive:
        dates.append(session["start_time"])
        totals["messages"] += session["user_message_count"]
        totals["duration_minutes"] += session["duration_minutes"]
        totals["input_tokens"] += session["input_tokens"]
        totals["output_tokens"] += session["output_tokens"]
        totals["git_commits"] += session["git_commits"]
        totals["git_pushes"] += session["git_pushes"]
        totals["interruptions"] += session["user_interruptions"]
        totals["tool_errors"] += session["tool_errors"]
        totals["lines_added"] += session["lines_added"]
        totals["lines_removed"] += session["lines_removed"]
        totals["files_modified"] += session["files_modified"]
        totals["sessions_using_task_agent"] += int(session["uses_task_agent"])
        totals["sessions_using_mcp"] += int(session["uses_mcp"])
        totals["sessions_using_web_search"] += int(session["uses_web_search"])
        totals["sessions_using_web_fetch"] += int(session["uses_web_fetch"])
        counters["tool_counts"].update(session["tool_counts"])
        counters["languages"].update(session["languages"])
        counters["projects"][session["project_path"]] += 1
        counters["tool_error_categories"].update(session["tool_error_categories"])
        response_times.extend(session["user_response_times"])
        hours.extend(session["message_hours"])

    active_days = len({d[:10] for d in dates})
    return {
        "platform": platform,
        "scope": scope,
        "total_sessions_scanned": scanned,
        "total_sessions": len(substantive),
        "raw_deduped_sessions": len(sessions),
        "date_range": {"start": min(dates)[:10] if dates else "", "end": max(dates)[:10] if dates else ""},
        "total_messages": totals["messages"],
        "total_duration_hours": round(totals["duration_minutes"] / 60, 2),
        "total_input_tokens": totals["input_tokens"],
        "total_output_tokens": totals["output_tokens"],
        "git_commits": totals["git_commits"],
        "git_pushes": totals["git_pushes"],
        "total_interruptions": totals["interruptions"],
        "total_tool_errors": totals["tool_errors"],
        "total_lines_added": totals["lines_added"],
        "total_lines_removed": totals["lines_removed"],
        "total_files_modified": totals["files_modified"],
        "sessions_using_task_agent": totals["sessions_using_task_agent"],
        "sessions_using_mcp": totals["sessions_using_mcp"],
        "sessions_using_web_search": totals["sessions_using_web_search"],
        "sessions_using_web_fetch": totals["sessions_using_web_fetch"],
        "days_active": active_days,
        "messages_per_day": round(totals["messages"] / active_days, 1) if active_days else 0,
        "median_response_time": round(median(response_times), 1),
        "avg_response_time": round(sum(response_times) / len(response_times), 1) if response_times else 0,
        "tool_counts": dict(counters["tool_counts"].most_common()),
        "languages": dict(counters["languages"].most_common()),
        "projects": dict(counters["projects"].most_common()),
        "tool_error_categories": dict(counters["tool_error_categories"].most_common()),
        "message_hours": hours,
        "multi_session_overlap": multi_session_overlap(substantive),
        "recent_sessions": substantive[:15],
        "longest_sessions": sorted(substantive, key=lambda s: s["duration_minutes"], reverse=True)[:10],
        "most_messages": sorted(substantive, key=lambda s: s["user_message_count"], reverse=True)[:10],
    }


def print_report(data: dict[str, Any]) -> None:
    title = "Claude Code Insights" if data["platform"] == "claude" else f"{data['platform'].title()} Session Insights"
    print(f"# {title}\n")
    print(f"Platform: {data['platform']} | Scope: {data['scope']}\n")
    label = f"{data['total_sessions_scanned']:,} files scanned | {data['total_sessions']:,} sessions analyzed"
    print(f"{label} | {data['total_messages']:,} messages | {round(data['total_duration_hours'])}h | {data['git_commits']} commits")
    print(f"{data['date_range']['start']} to {data['date_range']['end']}\n")

    print("## At a Glance\n")
    print(f"- Active days: {data['days_active']} ({data['messages_per_day']} messages/day)")
    print(f"- Tokens: {data['total_input_tokens']:,} input, {data['total_output_tokens']:,} output")
    print(f"- Code activity: +{data['total_lines_added']:,} / -{data['total_lines_removed']:,}, {data['total_files_modified']:,} modified-file touches")
    overlap = data["multi_session_overlap"]
    print(f"- Multi-session overlap: {overlap['overlap_events']} events across {overlap['sessions_involved']} sessions")
    print(f"- Tool errors: {data['total_tool_errors']} | interruptions: {data['total_interruptions']}\n")

    if data["tool_counts"]:
        print("## Top Tools\n")
        for name, count in list(data["tool_counts"].items())[:12]:
            print(f"- {name}: {count}")
        print()

    if data["projects"]:
        print("## Projects\n")
        for name, count in list(data["projects"].items())[:10]:
            print(f"- {name}: {count}")
        print()

    print("## Recent Sessions\n")
    for session in data["recent_sessions"]:
        prompt = (session.get("first_prompt") or "").replace("\n", " ")[:90]
        print(f"- {session['start_time'][:10]} | {session['duration_minutes']:5.0f} min | {session['user_message_count']:3d} msg | {prompt}")

    print("\nFacet-derived sections require semantic transcript analysis. Treat this report as deterministic metrics plus facet-ready session samples.")


def safe_name(value: str, fallback: str = "session") -> str:
    cleaned = "".join(ch if ch.isalnum() or ch in "-_." else "-" for ch in value.strip())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:80] or fallback


def compact_json(value: Any, limit: int = 2000) -> str:
    text = json.dumps(value, ensure_ascii=False, sort_keys=True)
    if len(text) > limit:
        return text[:limit] + "...<truncated>"
    return text


def compact_text(value: Any, limit: int = 500) -> str:
    text = " ".join(str(value or "").split())
    if len(text) > limit:
        return text[:limit] + "...<truncated>"
    return text


def format_claude_message(msg: dict[str, Any]) -> list[str]:
    ts = msg.get("timestamp", "")
    typ = msg.get("type", "?")
    lines = [f"### {ts} | {typ}", ""]
    content = msg_content(msg)
    if isinstance(content, str):
        if content.strip():
            lines.extend([content.strip(), ""])
    elif isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            btype = block.get("type")
            if btype == "text":
                text = str(block.get("text") or "").strip()
                if text:
                    lines.extend([text, ""])
            elif btype == "tool_use":
                lines.append(f"- tool_use: `{block.get('name', '?')}`")
                if block.get("input") is not None:
                    lines.append(f"  input: `{compact_json(block.get('input'))}`")
            elif btype == "tool_result":
                marker = " error" if block.get("is_error") else ""
                lines.append(f"- tool_result{marker}: `{compact_json(block.get('content', ''))}`")
        lines.append("")
    return lines


def format_claude_transcript(session: dict[str, Any]) -> str:
    path = Path(session["source_file"])
    rows = read_jsonl(path)
    target_id = session["session_id"]
    best_chain: list[dict[str, Any]] = []
    best_meta: dict[str, Any] | None = None
    for chain in build_claude_chains(rows):
        meta = claude_chain_meta(path, rows, chain)
        if not meta or meta["session_id"] != target_id:
            continue
        if (
            best_meta is None
            or meta["user_message_count"] > best_meta["user_message_count"]
            or (
                meta["user_message_count"] == best_meta["user_message_count"]
                and meta["duration_minutes"] > best_meta["duration_minutes"]
            )
        ):
            best_meta = meta
            best_chain = chain

    lines = [
        f"# Transcript: {target_id}",
        "",
        f"- platform: claude",
        f"- source_file: {path}",
        f"- project_path: {session.get('project_path', '')}",
        f"- start_time: {session.get('start_time', '')}",
        f"- duration_minutes: {session.get('duration_minutes', 0)}",
        f"- user_messages: {session.get('user_message_count', 0)}",
        f"- assistant_messages: {session.get('assistant_message_count', 0)}",
        "",
    ]
    for msg in best_chain:
        lines.extend(format_claude_message(msg))
    return "\n".join(lines)


def format_codex_transcript(session: dict[str, Any]) -> str:
    path = Path(session["source_file"])
    rows = read_jsonl(path)
    lines = [
        f"# Transcript: {session['session_id']}",
        "",
        f"- platform: codex",
        f"- source_file: {path}",
        f"- project_path: {session.get('project_path', '')}",
        f"- start_time: {session.get('start_time', '')}",
        f"- duration_minutes: {session.get('duration_minutes', 0)}",
        f"- user_messages: {session.get('user_message_count', 0)}",
        f"- assistant_messages: {session.get('assistant_message_count', 0)}",
        "",
    ]
    seen_user_texts = set()
    for row in rows:
        typ = row.get("type")
        payload = row.get("payload") or {}
        ts = payload.get("timestamp") or row.get("timestamp") or ""
        if typ == "event_msg":
            event_type = payload.get("type")
            if event_type == "exec_command_end":
                exit_code = payload.get("exit_code")
                if exit_code not in (None, 0, "0"):
                    command = payload.get("command") or []
                    command_text = " ".join(str(part) for part in command) if isinstance(command, list) else str(command)
                    output = payload.get("aggregated_output") or payload.get("stderr") or payload.get("stdout") or ""
                    lines.extend(
                        [
                            f"### {ts} | tool_failure",
                            "",
                            f"- command: `{compact_text(command_text, 240)}`",
                            f"- exit_code: {exit_code}",
                            f"- output: {compact_text(output, 500)}",
                            "",
                        ]
                    )
                continue
            if event_type != "user_message":
                continue
            text = str(payload.get("message") or "").strip()
            if text and not is_codex_internal_user_text(text) and text not in seen_user_texts:
                seen_user_texts.add(text)
                lines.extend([f"### {ts} | user", "", text, ""])
        elif typ == "response_item" and payload.get("type") == "message" and payload.get("role") == "user":
            text = codex_first_text(payload.get("content"))
            if text and not is_codex_internal_user_text(text) and text not in seen_user_texts:
                seen_user_texts.add(text)
                lines.extend([f"### {ts} | user", "", text, ""])
        elif typ == "response_item" and payload.get("type") == "message" and payload.get("role") == "assistant":
            parts = []
            for block in payload.get("content") or []:
                if isinstance(block, dict):
                    text = block.get("text") or block.get("content")
                    if text:
                        parts.append(str(text))
            if parts:
                lines.extend([f"### {ts} | assistant", "", "\n".join(parts), ""])
    return "\n".join(lines)


def analysis_template(session: dict[str, Any], transcript_rel: str) -> str:
    return f"""# Session Analysis: {session['session_id']}

- transcript: `{transcript_rel}`
- project: `{session.get('project_path', '')}`
- start: `{session.get('start_time', '')}`
- duration_minutes: {session.get('duration_minutes', 0)}
- user_messages: {session.get('user_message_count', 0)}
- tool_errors: {session.get('tool_errors', 0)}
- interruptions: {session.get('user_interruptions', 0)}
- top_tools: {", ".join(list((session.get("tool_counts") or {}).keys())[:8]) or "none"}

## Goal

TODO: infer the user's real goal from transcript evidence. Keep this concrete.

## Outcome

TODO: identify the likely outcome and confidence. Do not claim success unless the transcript supports it.

## Decisions

TODO: list important decisions, trade-offs, or rejected alternatives.

## Learnings

TODO: list reusable technical or workflow learnings from this session.

## Friction

TODO: identify blockers, repeated clarification, failed tools, stale assumptions, or scope churn.

## Effective Patterns

TODO: identify what worked well and why.

## Prompt Quality

TODO: evaluate the user's prompt/context/scoping/timing. Include one concrete before/after improvement if useful.

## Workflow Signals

TODO: connect deterministic counters to transcript evidence.

## Recommendation

TODO: write concrete behavior changes for future sessions. Include copyable prompts or AGENTS.md rule candidates when supported by evidence.
"""


def workflow_summary_template(platform: str, scope: str, data: dict[str, Any]) -> str:
    return f"""# Workflow Summary

Scope: `{platform} {scope}`

This file is intentionally a semantic-analysis workspace. Deterministic metrics are listed below; the recurring problems, fixes, and evidence sections should be filled by the AI agent after reading `analyses/*.md` and the referenced transcripts.

## Deterministic Metrics

- Sessions scanned: {data['total_sessions_scanned']}
- Deduped sessions: {data['raw_deduped_sessions']}
- Analyzed sessions: {data['total_sessions']}
- Date range: {data['date_range']['start']} to {data['date_range']['end']}
- Messages: {data['total_messages']}
- Code activity: +{data['total_lines_added']} / -{data['total_lines_removed']}, {data['total_files_modified']} file touches
- Git commits: {data['git_commits']}
- Tool errors: {data['total_tool_errors']}
- Interruptions: {data['total_interruptions']}

## Recurring Problems

TODO: synthesize from `analyses/*.md`.

## What Worked

TODO: identify repeated effective patterns, not generic praise.

## High-Leverage Fixes

TODO: synthesize concrete behavior changes from `analyses/*.md`.

## AGENTS.md Candidates

TODO: pasteable durable instructions, each with why/evidence. Do not include temporary stats.

## Skill Candidates

TODO: identify repeated operations that should become reusable skills. For each candidate include trigger, why it recurs, required evidence, core steps, validation, and non-goals. Do not propose skills for one-off facts.

## Copyable Prompts

TODO: prompts the user can paste into future Codex sessions.

## On The Horizon

TODO: ambitious but realistic next-step workflows grounded in evidence.

## Evidence

TODO: cite representative transcript and analysis files.
"""


def analysis_instructions(platform: str, scope: str) -> str:
    return f"""# Session Insights Analysis Instructions

Platform: `{platform}`
Scope: `{scope}`

The Python script prepared evidence only. The AI agent must perform the semantic analysis.

## Required Process

1. Read `manifest.json` and `session-insights-data.json`.
2. Read each `transcripts/*.md` file, or process them in batches if the set is large.
3. Fill the matching `analyses/*.md` file for every transcript considered.
4. Synthesize `workflow-summary.md` from the analyses.
5. Write `report.json` with structured insights.
6. Write `report.html` as a readable local report.

## Analysis Principles

- Use only evidence from the metrics, transcripts, and analyses.
- Do not hard-code fixed workflow categories. Let the transcript evidence drive the grouping.
- Separate deterministic metrics from AI-generated interpretation.
- Prefer repeated patterns over isolated anecdotes.
- Be conservative when evidence is weak or mixed.
- Distinguish model-side friction, user/workflow-side friction, and external/environmental friction.
- Produce concrete improvements the user can apply in future sessions.
- Include copyable prompts and AGENTS.md candidates only when supported by evidence.

## Per-Session Analysis Targets

For each session, identify:

- user's actual goal
- outcome and confidence
- decisions and trade-offs
- reusable learnings
- friction points and likely cause
- effective patterns
- prompt quality feedback
- one or more concrete recommendations when warranted

## Final Report Shape

`workflow-summary.md` should include:

- At a Glance
- Work Mix, grouped by evidence-derived themes
- What Worked
- Where Things Go Wrong
- High-Leverage Fixes
- AGENTS.md Candidates
- Skill Candidates
- Copyable Prompts
- On The Horizon
- Evidence

`report.json` should include:

```json
{{
  "at_a_glance": {{
    "working": "string",
    "hindering": "string",
    "quick_wins": "string",
    "ambitious_workflows": "string"
  }},
  "work_themes": [{{"name": "string", "session_count": 0, "evidence": ["string"]}}],
  "wins": [{{"title": "string", "detail": "string", "evidence": ["string"]}}],
  "friction": [{{"title": "string", "detail": "string", "attribution": "user-actionable|ai-capability|environmental|mixed", "evidence": ["string"]}}],
  "agents_md_candidates": [{{"text": "string", "why": "string", "evidence": ["string"]}}],
  "skill_candidates": [{{"name": "string", "trigger": "string", "why": "string", "steps": ["string"], "validation": ["string"], "non_goals": ["string"], "evidence": ["string"]}}],
  "copyable_prompts": [{{"title": "string", "prompt": "string", "why": "string"}}],
  "on_the_horizon": [{{"title": "string", "how_to_try": "string", "copyable_prompt": "string"}}]
}}
```
"""


def export_workflow_artifacts(
    platform: str,
    scope: str,
    data: dict[str, Any],
    sessions: list[dict[str, Any]],
    export_dir: Path,
    export_limit: int,
) -> Path:
    substantive = [s for s in sessions if s["user_message_count"] >= 2 and s["duration_minutes"] >= 1]
    selected = substantive if export_limit <= 0 else substantive[:export_limit]
    transcripts_dir = export_dir / "transcripts"
    analyses_dir = export_dir / "analyses"
    transcripts_dir.mkdir(parents=True, exist_ok=True)
    analyses_dir.mkdir(parents=True, exist_ok=True)

    manifest_sessions = []
    for idx, session in enumerate(selected, start=1):
        slug = safe_name(f"{idx:04d}-{session['start_time'][:10]}-{session['session_id'][:12]}")
        transcript_path = transcripts_dir / f"{slug}.md"
        analysis_path = analyses_dir / f"{slug}.md"
        if platform == "claude":
            transcript_text = format_claude_transcript(session)
        else:
            transcript_text = format_codex_transcript(session)
        transcript_path.write_text(transcript_text, encoding="utf-8")
        analysis_path.write_text(
            analysis_template(session, str(transcript_path.relative_to(export_dir))),
            encoding="utf-8",
        )
        manifest_sessions.append(
            {
                "session_id": session["session_id"],
                "start_time": session["start_time"],
                "project_path": session.get("project_path", ""),
                "transcript": str(transcript_path),
                "analysis": str(analysis_path),
            }
        )

    (export_dir / "session-insights-data.json").write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    (export_dir / "manifest.json").write_text(
        json.dumps(
            {
                "platform": platform,
                "scope": scope,
                "session_count": len(selected),
                "sessions": manifest_sessions,
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    (export_dir / "analysis-instructions.md").write_text(
        analysis_instructions(platform, scope),
        encoding="utf-8",
    )
    (export_dir / "workflow-summary.md").write_text(
        workflow_summary_template(platform, scope, data),
        encoding="utf-8",
    )
    return export_dir


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate an /insights-style session report.")
    parser.add_argument("--platform", required=True, choices=["claude", "codex"], help="Session provider adapter.")
    parser.add_argument("--scope", default="all", help="all, path, recent:N, since:YYYY-MM-DD, or project:TEXT")
    parser.add_argument("--diagnose-workflow", dest="diagnose_workflow", action="store_true", default=True, help="Export per-session transcripts and analysis templates. This is the default.")
    parser.add_argument("--metrics-only", dest="diagnose_workflow", action="store_false", help="Only print deterministic metrics and write the usage-data JSON.")
    parser.add_argument("--export-dir", help="Directory for workflow diagnosis artifacts. Defaults to /tmp/session-insights/<timestamp>.")
    parser.add_argument("--export-limit", type=int, default=0, help="Maximum sessions to export; 0 means all analyzed sessions.")
    args = parser.parse_args()

    home, scanned, sessions = scan_sessions(args.platform, args.scope)
    data = aggregate(args.platform, args.scope, scanned, sessions)
    out_dir = home / "usage-data"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "session-insights-data.json"
    out_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print_report(data)
    print(f"\nData JSON: {out_path}")
    if args.diagnose_workflow:
        export_dir = Path(
            args.export_dir
            or f"/tmp/session-insights/{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        ).expanduser()
        created = export_workflow_artifacts(
            args.platform,
            args.scope,
            data,
            sessions,
            export_dir,
            args.export_limit,
        )
        print(f"Workflow artifacts: {created}")


if __name__ == "__main__":
    main()
