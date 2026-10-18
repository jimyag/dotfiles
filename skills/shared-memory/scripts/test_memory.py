import concurrent.futures
import json
from pathlib import Path
import select
import sqlite3
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).with_name("memory.py")
REPO = next((path for path in SCRIPT.resolve().parents if (path / ".git").exists()), Path.cwd())


class MemoryCLITests(unittest.TestCase):
    def setUp(self):
        temporary_root = REPO / "tmp"
        temporary_root.mkdir(parents=True, exist_ok=True)
        temporary = tempfile.TemporaryDirectory(prefix="shared-memory-tests-", dir=temporary_root)
        self.addCleanup(temporary.cleanup)
        self.workspace = Path(temporary.name)
        self.codex_home = self.workspace / "codex-home"
        self.claude_home = self.workspace / "claude-home"
        self.root = self.workspace / "store"
        self.project = self.workspace / "project"
        self.project.mkdir()
        self.git("init", "--quiet", self.project)

    def run_cli(self, *arguments, body=None, success=True, root=None):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--root", str(root or self.root),
             "--codex-home", str(self.codex_home), "--claude-home", str(self.claude_home),
             *map(str, arguments)],
            input=body,
            text=True,
            capture_output=True,
            timeout=15,
        )
        if not success:
            self.assertNotEqual(result.returncode, 0, result.stdout)
            self.assertTrue(result.stderr.strip())
            return result
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def git(self, *arguments):
        result = subprocess.run(
            ["git", "-c", "init.defaultBranch=main", "-c", "commit.gpgsign=false",
             "-c", "core.hooksPath=/dev/null", "-c", "user.name=Memory Tests",
             "-c", "user.email=memory-tests@example.invalid", *map(str, arguments)],
            capture_output=True, text=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def metadata(self, saved):
        header = Path(saved["path"]).read_text(encoding="utf-8").removeprefix("---\n").split("\n---\n", 1)[0]
        return json.loads(header)

    def save(self, key, title, body, *, agent="codex", project=None, root=None, expect_hash=None):
        scope = ["--global"] if project is None else ["--project", str(project)]
        expected = [] if expect_hash is None else ["--expect-hash", expect_hash]
        return self.run_cli(
            "save", "--agent", agent, "--key", key, "--title", title, *scope, *expected,
            body=body, root=root,
        )

    def forget(self, saved):
        return self.run_cli("forget", saved["id"], "--expect-hash", self.metadata(saved)["content_hash"])

    def gated_cli(self, hook, *arguments, root=None):
        # Stop at the real CLI boundary so concurrent writes and interruptions have deterministic order.
        process = subprocess.Popen(
            [sys.executable, "-c", """
import contextlib
import runpy
import sys

namespace = runpy.run_path(sys.argv[1])["main"].__globals__
original = namespace[sys.argv[2]]

def wait_for_release():
    print("ready", flush=True)
    if sys.stdin.readline() != "continue\\n":
        raise RuntimeError("gate was not released")

if sys.argv[2] == "locked":
    @contextlib.contextmanager
    def gated(*args, **kwargs):
        wait_for_release()
        with original(*args, **kwargs):
            yield
else:
    def gated(*args, **kwargs):
        wait_for_release()
        return original(*args, **kwargs)

namespace[sys.argv[2]] = gated
sys.argv = [sys.argv[1], *sys.argv[3:]]
namespace["main"]()
""", str(SCRIPT), hook, "--root", str(root or self.root), *map(str, arguments)],
            stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        )

        def cleanup():
            if process.poll() is None:
                process.kill()
            process.communicate(timeout=5)

        self.addCleanup(cleanup)
        self.assertTrue(select.select([process.stdout], [], [], 10)[0], "CLI did not reach gate")
        self.assertEqual(process.stdout.readline(), "ready\n")
        return process

    def file_state(self, *paths):
        return [(path.read_bytes(), path.stat().st_mtime_ns) for path in paths]

    def test_save_is_stable_across_agents_and_explicitly_restores_forgotten_notes(self):
        first = self.save("build-command", "Build command", "Run the original build.")
        self.assertEqual(first["status"], "saved")
        header, body = Path(first["path"]).read_text(encoding="utf-8").removeprefix("---\n").split("\n---\n", 1)
        metadata = json.loads(header)
        self.assertEqual(metadata["schema"], 1)
        self.assertEqual(metadata["id"], first["id"])
        self.assertEqual(body.strip(), "Run the original build.")
        self.assertEqual(
            self.save("build-command", "Build command", "Run the original build.")["status"],
            "unchanged",
        )
        updated = self.save(
            "build-command", "Corrected command", "Run the corrected build.", agent="claude-code",
            expect_hash=metadata["content_hash"],
        )
        self.assertEqual(updated["id"], first["id"])
        self.assertEqual(updated["status"], "saved")
        self.assertEqual(len(list((self.root / "notes").glob("*.md"))), 1)
        self.assertEqual(
            self.run_cli("search", "corrected")[0]["title"], "Corrected command",
        )
        self.assertEqual(
            self.forget(first), {"id": first["id"], "status": "forgotten"},
        )
        self.assertFalse(Path(first["path"]).exists())
        body_file = self.workspace / "restored.md"
        body_file.write_text("Run the restored build.\n", encoding="utf-8")
        restored = self.run_cli(
            "save", "--agent", "codex", "--key", "build-command", "--title", "Restored command",
            "--global", "--restore", "--source", "conversation:example", "--file", body_file,
        )
        self.assertEqual(restored["id"], first["id"])
        self.assertEqual(restored["status"], "saved")
        self.assertEqual([item["id"] for item in self.run_cli("search", "restored")], [first["id"]])

    def test_project_search_includes_global_and_excludes_other_projects(self):
        other_project = self.workspace / "other-project"
        other_project.mkdir()
        self.git("init", "--quiet", other_project)
        global_note = self.save("global", "Global guidance", "scope-marker global")
        project_note = self.save("project", "Project guidance", "scope-marker project", project=self.project)
        other_note = self.save("project", "Other guidance", "scope-marker other", project=other_project)
        self.assertNotEqual(project_note["id"], other_note["id"])
        self.assertEqual(
            {item["id"] for item in self.run_cli("search", "scope-marker")},
            {global_note["id"], project_note["id"], other_note["id"]},
        )
        self.assertEqual(
            {item["id"] for item in self.run_cli("search", "scope-marker", "--project", self.project)},
            {global_note["id"], project_note["id"]},
        )

    def test_stale_updates_and_deletes_leave_current_memory_unchanged(self):
        original = self.save("shared-fact", "Shared fact", "Initial conclusion.")
        old_hash = self.metadata(original)["content_hash"]
        updated = self.save("shared-fact", "Shared fact", "Corrected conclusion.",
                            agent="claude-code", expect_hash=old_hash)
        current_hash = self.metadata(updated)["content_hash"]
        note = Path(updated["path"])
        summary = self.root / "memory_summary.md"
        state = self.file_state(note, summary)
        save_arguments = ("save", "--agent", "codex", "--key", "shared-fact",
                          "--title", "Shared fact", "--global")
        for expected in ([], ["--expect-hash", old_hash]):
            with self.subTest(expected=expected):
                self.run_cli(*save_arguments, *expected, body="Stale conclusion.", success=False)
                self.run_cli("forget", original["id"], *expected, success=False)
                self.assertEqual(self.file_state(note, summary), state)
        for expected in ([], ["--expect-hash", current_hash]):
            with self.subTest(restore_expected=expected):
                self.run_cli(*save_arguments, "--restore", *expected,
                             body="Unapproved replacement.", success=False)
                self.assertEqual(self.file_state(note, summary), state)
        self.assertEqual(self.save("shared-fact", "Shared fact", "Corrected conclusion.")["status"],
                         "unchanged")
        self.assertEqual(self.file_state(note, summary), state)
        self.run_cli("forget", original["id"], "--expect-hash", current_hash)
        self.assertEqual(self.run_cli("forget", original["id"])["status"], "forgotten")
        for expected in ([], ["--expect-hash", old_hash], ["--expect-hash", current_hash]):
            with self.subTest(deleted_expected=expected):
                result = self.run_cli(*save_arguments, *expected, body="Stale conclusion.")
                self.assertEqual(result["status"], "forgotten")
                self.assertFalse(note.exists())
                self.assertEqual(self.run_cli("search", "conclusion"), [])
        self.run_cli("save", "--agent", "codex", "--key", "never-existed", "--title", "New",
                     "--global", "--restore", body="Not a deleted memory.", success=False)
        self.run_cli("save", "--agent", "codex", "--key", "never-existed", "--title", "New",
                     "--global", "--expect-hash", old_hash, body="Stale creation.", success=False)

    def test_concurrent_corrections_allow_only_one_writer_with_the_same_hash(self):
        original = self.save("race-fact", "Race fact", "Original conclusion.")
        expected = self.metadata(original)["content_hash"]

        def correct(agent):
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--root", str(self.root), "save", "--agent", agent,
                 "--key", "race-fact", "--title", "Race fact", "--global", "--expect-hash", expected],
                input=f"Winning conclusion from {agent}.", text=True, capture_output=True, timeout=15,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(correct, ("codex", "claude-code")))
        self.assertEqual(sum(result.returncode == 0 for result in results), 1,
                         [(result.returncode, result.stderr) for result in results])
        winner = next(agent for agent, result in zip(("codex", "claude-code"), results)
                      if result.returncode == 0)
        current = self.run_cli("search", "Winning conclusion")
        self.assertEqual(len(current), 1)
        self.assertEqual(current[0]["agent"], winner)
        self.assertIn(winner, current[0]["excerpt"])
        self.assertEqual(len(list((self.root / "notes").glob("*.md"))), 1)

    def test_project_identity_is_shared_by_subdirectories_and_linked_worktrees(self):
        self.git("-C", self.project, "commit", "--quiet", "--allow-empty", "-m", "Test repository")
        worktree = self.project / ".worktrees" / "linked-worktree"
        self.git("-C", self.project, "worktree", "add", "--quiet", "--detach", worktree, "HEAD")
        subdirectory = self.project / "subdirectory"
        linked_subdirectory = worktree / "subdirectory"
        subdirectory.mkdir()
        linked_subdirectory.mkdir()
        original = self.save("worktree-guidance", "Worktree guidance", "Shared repository fact.",
                             project=self.project)
        for project in (subdirectory, worktree, linked_subdirectory):
            with self.subTest(project=project):
                same = self.save("worktree-guidance", "Worktree guidance", "Shared repository fact.",
                                 project=project)
                self.assertEqual((same["id"], same["status"]), (original["id"], "unchanged"))
                self.assertEqual([item["id"] for item in self.run_cli(
                    "search", "Shared repository", "--project", project)], [original["id"]])
        updated = self.save("worktree-guidance", "Worktree guidance", "Corrected repository fact.",
                            project=linked_subdirectory,
                            expect_hash=self.metadata(original)["content_hash"])
        self.assertEqual(updated["id"], original["id"])
        self.assertEqual(self.metadata(updated)["scope"], str(self.project.resolve()))
        self.assertEqual([item["id"] for item in self.run_cli(
            "search", "Corrected repository", "--project", self.project)], [original["id"]])

    def test_search_uses_keys_prioritizes_project_matches_and_limits_results(self):
        key_match = self.save("ranking-marker", "Key match", "First project fact.", project=self.project)
        title_match = self.save("title-match", "ranking-marker title", "Second project fact.",
                                project=self.project)
        body_match = self.save("body-match", "Body match", "ranking-marker body", project=self.project)
        global_match = self.save("global-match", "ranking-marker global", "Newest global fact.")
        matches = self.run_cli("search", "ranking-marker", "--project", self.project)
        self.assertEqual({item["id"] for item in matches[:2]}, {key_match["id"], title_match["id"]})
        self.assertEqual([item["id"] for item in matches[2:]], [body_match["id"], global_match["id"]])
        self.assertEqual(len(self.run_cli("search", "ranking-marker", "--project", self.project,
                                         "--limit", 1)), 1)
        recent = self.run_cli("list", "--project", self.project, "--limit", 2)
        self.assertEqual([item["id"] for item in recent], [body_match["id"], title_match["id"]])
        self.assertTrue(all("content_hash" in item and "path" in item for item in matches + recent))
        for command in (("search", "ranking-marker"), ("list",)):
            for limit in ("0", "-1", "not-a-number"):
                with self.subTest(command=command, limit=limit):
                    self.run_cli(*command, "--limit", limit, success=False)

    def test_default_limit_and_project_filter_apply_to_search_and_list(self):
        for number in range(21):
            self.save(f"limited-{number}", f"Limited note {number}", f"limit-marker {number}")
        other_project = self.workspace / "other-project"
        self.git("init", "--quiet", other_project)
        excluded = self.save("excluded", "Excluded note", "limit-marker other", project=other_project)
        for command in (("search", "limit-marker"), ("list",)):
            with self.subTest(command=command):
                self.assertEqual(len(self.run_cli(*command)), 20)
                all_matches = self.run_cli(*command, "--project", self.project, "--limit", 100)
                self.assertEqual(len(all_matches), 21)
                self.assertNotIn(excluded["id"], {item["id"] for item in all_matches})

    def test_tracked_source_requires_current_ack_and_detects_deletion_and_reappearance(self):
        source = self.workspace / "tracked.md"
        source.write_text("Original native conclusion.\n", encoding="utf-8")
        arguments = ("track", "--source", source, "--global")
        self.run_cli(*arguments)
        initial = self.run_cli("pending")
        self.assertEqual(len(initial), 1)
        original = initial[0]
        self.assertEqual(original["status"], "pending")
        self.assertEqual(original["source"], str(source.resolve()))
        self.assertEqual(original["scope"], "global")
        self.run_cli(*arguments)
        self.assertEqual(self.run_cli("pending"), initial)
        self.run_cli("ack", original["id"], "--expect-hash", original["content_hash"])
        self.assertEqual(self.run_cli("pending"), [])
        self.run_cli(*arguments)
        self.assertEqual(self.run_cli("pending"), [])
        source.write_text("Corrected native conclusion.\n", encoding="utf-8")
        changed = self.run_cli("pending")[0]
        self.assertEqual(changed["id"], original["id"])
        self.assertEqual(changed["status"], "changed")
        self.assertNotEqual(changed["content_hash"], original["content_hash"])
        self.run_cli("ack", original["id"], "--expect-hash", original["content_hash"], success=False)
        self.assertEqual(self.run_cli("pending"), [changed])
        self.run_cli("ack", changed["id"], "--expect-hash", changed["content_hash"])
        source.write_text("", encoding="utf-8")
        cleared = self.run_cli("pending")[0]
        self.assertEqual(cleared["status"], "changed")
        self.assertNotEqual(cleared["content_hash"], changed["content_hash"])
        self.run_cli("ack", cleared["id"], "--expect-hash", cleared["content_hash"])
        self.assertEqual(self.run_cli("pending"), [])
        source.unlink()
        missing = self.run_cli("pending")[0]
        self.assertEqual(missing["status"], "missing")
        self.run_cli("ack", missing["id"], "--expect-hash", changed["content_hash"], success=False)
        self.run_cli("ack", missing["id"], "--expect-hash", missing["content_hash"])
        self.assertEqual(self.run_cli("pending"), [])
        source.write_text("Corrected native conclusion.\n", encoding="utf-8")
        reappeared = self.run_cli("pending")
        self.assertEqual(len(reappeared), 1)
        self.assertEqual(reappeared[0]["id"], original["id"])
        self.assertEqual(self.run_cli("list"), [])

    def test_tracked_directory_detects_file_changes_and_respects_project_scope(self):
        native = self.workspace / "tracked-directory"
        native.mkdir()
        first = native / "first.md"
        first.write_text("First fact.\n", encoding="utf-8")
        other_project = self.workspace / "other-project"
        self.git("init", "--quiet", other_project)
        self.run_cli("track", "--source", native, "--project", self.project)
        self.run_cli("track", "--source", first, "--project", other_project)
        self.run_cli("track", "--source", first, "--global")
        all_pending = self.run_cli("pending")
        selected = self.run_cli("pending", "--project", self.project)
        self.assertEqual(len(all_pending), 3)
        self.assertEqual(len(selected), 2)
        self.assertEqual({item["scope"] for item in selected}, {"global", str(self.project.resolve())})
        directory = next(item for item in selected if item["source"] == str(native.resolve()))
        self.run_cli("ack", directory["id"], "--expect-hash", directory["content_hash"])
        second = native / "second.md"
        second.write_text("Second fact.\n", encoding="utf-8")
        changed = next(item for item in self.run_cli("pending") if item["id"] == directory["id"])
        self.assertNotEqual(changed["content_hash"], directory["content_hash"])
        self.run_cli("ack", changed["id"], "--expect-hash", changed["content_hash"])
        first.unlink()
        changed_again = next(item for item in self.run_cli("pending") if item["id"] == directory["id"])
        self.assertNotEqual(changed_again["content_hash"], changed["content_hash"])

    def test_tracking_rejects_unsafe_sources_and_corrupt_registry_without_overwriting_it(self):
        source = self.workspace / "tracked.md"
        source.write_text("Retained native fact.\n", encoding="utf-8")
        self.run_cli("track", "--source", source, "--global")
        pending = self.run_cli("pending")[0]
        registry = self.root / "sources.json"
        original = self.file_state(registry)
        linked = self.workspace / "linked.md"
        linked.symlink_to(source)
        wrong_type = self.workspace / "source.txt"
        wrong_type.write_text("Not Markdown.\n", encoding="utf-8")
        for unsafe in (linked, wrong_type, self.root, self.workspace, self.workspace / "missing.md"):
            with self.subTest(source=unsafe):
                self.run_cli("track", "--source", unsafe, "--global", success=False)
                self.assertEqual(self.file_state(registry), original)
        for invalid in ("invalid", "0" * 63, "A" * 64):
            with self.subTest(hash=invalid):
                self.run_cli("ack", pending["id"], "--expect-hash", invalid, success=False)
                self.assertEqual(self.file_state(registry), original)
        source.unlink()
        source.symlink_to(wrong_type)
        self.run_cli("pending", success=False)
        self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"], success=False)
        self.assertEqual(self.file_state(registry), original)
        external_registry = self.workspace / "registry.json"
        registry.replace(external_registry)
        registry.symlink_to(external_registry)
        self.run_cli("pending", success=False)
        self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"], success=False)
        self.assertEqual(self.file_state(external_registry), original)
        registry.unlink()
        registry.write_text('{"schema": 1, "sources": []}\n', encoding="utf-8")
        malformed = self.file_state(registry)
        self.run_cli("pending", success=False)
        self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"], success=False)
        self.assertEqual(self.file_state(registry), malformed)

    def test_empty_native_file_can_be_tracked_but_not_imported_as_a_fact(self):
        source = self.workspace / "empty.md"
        source.touch()
        self.run_cli("track", "--source", source, "--global")
        pending = self.run_cli("pending")[0]
        self.assertEqual(pending["status"], "pending")
        self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"])
        self.assertEqual(self.run_cli("pending"), [])
        self.run_cli("sync", "--agent", "codex", "--source", source, "--global", success=False)
        self.assertEqual(self.run_cli("list"), [])

    def test_pending_discovers_unregistered_legacy_v2_databases_and_new_claude_projects(self):
        legacy = self.codex_home / "memories" / "MEMORY.md"
        archive = self.codex_home / "memories_v2" / "rollout_summaries" / "example.md"
        claude = self.claude_home / "projects" / "new-project" / "memory" / "note.md"
        for path in (legacy, archive, claude):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("A native fact.\n")
        database = self.codex_home / "memories_v2_1.sqlite"
        database.touch()
        expected = {str(legacy), str(archive.parent), str(claude.parent), str(database)}
        discovered = self.run_cli("pending")
        self.assertEqual({item["source"] for item in discovered}, expected)
        self.assertTrue(all(item["status"] == "untracked" for item in discovered))
        self.assertFalse(self.root.exists())
        self.run_cli("track", "--source", legacy, "--global")
        pending = self.run_cli("pending")
        self.assertEqual(len(pending), 4)
        self.assertEqual(next(item for item in pending if item["source"] == str(legacy))["status"], "pending")
        self.assertIsNone(next(item for item in pending if item["source"] == str(claude.parent))["scope"])
        self.run_cli("read-source", pending[0]["id"], "--thread-id", "not-sqlite", success=False)
        later = self.claude_home / "projects" / "later-project" / "memory" / "new.md"
        later.parent.mkdir(parents=True)
        later.write_text("New project memory.\n")
        self.assertEqual(len(self.run_cli("pending")), 5)

    def test_sqlite_wal_changes_are_reviewable_and_ack_checks_semantic_snapshot(self):
        source = self.workspace / "memories_1.sqlite"
        with sqlite3.connect(source) as writer:
            writer.execute("PRAGMA journal_mode=WAL")
            writer.execute("CREATE TABLE stage1_outputs (thread_id TEXT PRIMARY KEY, raw_memory TEXT, "
                           "rollout_summary TEXT, usage_count INTEGER)")
            writer.execute("INSERT INTO stage1_outputs VALUES ('thread-a', 'Initial fact', 'Summary', 0)")
            writer.commit()
            self.run_cli("track", "--source", source, "--global")
            pending = self.run_cli("pending")[0]
            manifest = self.run_cli("read-source", pending["id"])
            self.assertEqual(manifest["content_hash"], pending["content_hash"])
            self.assertEqual([item["thread_id"] for item in manifest["records"]], ["thread-a"])
            self.assertNotIn("raw_memory", manifest["records"][0])
            detail = self.run_cli("read-source", pending["id"], "--thread-id", "thread-a")
            self.assertEqual(detail["records"][0]["raw_memory"], "Initial fact")
            self.run_cli("read-source", pending["id"], "--thread-id", "missing", success=False)
            self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"])
            state = self.file_state(source)
            self.assertEqual(self.run_cli("pending"), [])
            self.assertEqual(self.file_state(source), state)
            writer.execute("UPDATE stage1_outputs SET usage_count=1")
            writer.commit()
            self.assertEqual(self.run_cli("pending"), [])
            writer.execute("UPDATE stage1_outputs SET raw_memory='Corrected fact'")
            writer.execute("INSERT INTO stage1_outputs VALUES ('thread-b', 'New fact', 'New summary', 0)")
            writer.commit()
            changed = self.run_cli("pending")[0]
            self.assertEqual(changed["status"], "changed")
            self.assertEqual(changed["changed_threads"], ["thread-a", "thread-b"])
            self.assertEqual(changed["removed_threads"], [])
            self.run_cli("ack", pending["id"], "--expect-hash", pending["content_hash"], success=False)
            current = self.run_cli("read-source", changed["id"])
            self.assertEqual(len(current["records"]), 2)
            self.assertEqual(current["content_hash"], changed["content_hash"])
            self.run_cli("ack", changed["id"], "--expect-hash", changed["content_hash"])
            self.assertEqual(self.run_cli("pending"), [])
            writer.execute("DELETE FROM stage1_outputs WHERE thread_id='thread-a'")
            writer.commit()
            removed = self.run_cli("pending")[0]
            self.assertEqual(removed["changed_threads"], [])
            self.assertEqual(removed["removed_threads"], ["thread-a"])
            self.run_cli("ack", removed["id"], "--expect-hash", removed["content_hash"])
        with sqlite3.connect(source) as writer:
            writer.execute("VACUUM")
        self.assertEqual(self.run_cli("pending"), [])

    def test_invalid_sqlite_schema_does_not_register_or_ack(self):
        source = self.workspace / "invalid.sqlite"
        with sqlite3.connect(source) as writer:
            writer.execute("CREATE TABLE unrelated (value TEXT)")
        self.run_cli("track", "--source", source, "--global", success=False)
        self.assertFalse((self.root / "sources.json").exists())
        self.run_cli("read-source", "0" * 64, success=False)

    def test_native_sync_is_idempotent_updates_and_respects_forget(self):
        native = self.workspace / "native"
        native.mkdir()
        source = native / "preferences.md"
        source.write_text("# Native preference\n\nnative-marker first\n", encoding="utf-8")
        arguments = ("sync", "--agent", "claude-code", "--source", native, "--project", self.project)
        self.assertEqual(self.run_cli(*arguments), {"saved": 1, "unchanged": 0, "forgotten": 0})
        self.assertEqual(self.run_cli("pending"), [])
        original = self.run_cli("search", "native-marker")[0]
        self.assertEqual(
            self.run_cli("sync", "--agent", "claude-code", "--source", source, "--project", self.project),
            {"saved": 0, "unchanged": 1, "forgotten": 0},
        )
        source.write_text("# Native preference\n\nnative-marker corrected\n", encoding="utf-8")
        self.assertEqual(self.run_cli(*arguments), {"saved": 1, "unchanged": 0, "forgotten": 0})
        updated = self.run_cli("search", "corrected")[0]
        self.assertEqual(updated["id"], original["id"])
        self.assertIn("corrected", updated["excerpt"])
        self.forget(original)
        source.write_text("# Native preference\n\nnative-marker changed again\n", encoding="utf-8")
        self.assertEqual(self.run_cli(*arguments), {"saved": 0, "unchanged": 0, "forgotten": 1})
        self.assertEqual(
            self.run_cli("sync", "--agent", "codex", "--source", source, "--project", self.project),
            {"saved": 0, "unchanged": 0, "forgotten": 1},
        )
        self.assertEqual(self.run_cli("search", "native-marker"), [])
        self.assertFalse(Path(original["path"]).exists())
        self.assertNotIn(original["id"], (self.root / "memory_summary.md").read_text(encoding="utf-8"))

    def test_sync_reads_source_after_acquiring_write_lock(self):
        source = self.workspace / "native.md"
        source.write_text("old-marker\n", encoding="utf-8")
        arguments = ("sync", "--agent", "codex", "--source", source, "--global")
        paused = self.gated_cli("locked", *arguments)
        source.write_text("new-marker\n", encoding="utf-8")
        self.assertEqual(self.run_cli(*arguments), {"saved": 1, "unchanged": 0, "forgotten": 0})
        output, error = paused.communicate("continue\n", timeout=15)
        self.assertEqual(paused.returncode, 0, error)
        self.assertEqual(len(self.run_cli("search", "new-marker")), 1)
        self.assertEqual(self.run_cli("search", "old-marker"), [])
        self.assertEqual(json.loads(output), {"saved": 0, "unchanged": 1, "forgotten": 0})

    def test_retry_after_interrupted_write_repairs_summary_without_refreshing_unchanged_files(self):
        for command in ("save", "sync"):
            with self.subTest(command=command):
                root = self.workspace / command
                baseline = self.save("baseline", "Existing note", "Keep this note.", root=root)
                summary = root / "memory_summary.md"
                original_summary = summary.read_bytes()
                source = self.workspace / f"{command}-recovered.md"
                source.write_text("recovery-marker\n", encoding="utf-8")
                arguments = (
                    ("save", "--agent", "codex", "--key", "recovered", "--title", "Recovered note",
                     "--global", "--file", source)
                    if command == "save" else
                    ("sync", "--agent", "codex", "--source", source, "--global")
                )
                interrupted = self.gated_cli("rebuild_summary", *arguments, root=root)
                self.assertEqual(summary.read_bytes(), original_summary)
                interrupted.terminate()
                interrupted.communicate(timeout=5)
                self.assertLess(interrupted.returncode, 0)
                recovered = self.run_cli("search", "recovery-marker", root=root)[0]
                note = Path(recovered["path"])
                original_note = self.file_state(note)
                expected = {"saved": 0, "unchanged": 1, "forgotten": 0}
                retried = self.run_cli(*arguments, root=root)
                self.assertEqual(retried["status"] if command == "save" else retried,
                                 "unchanged" if command == "save" else expected)
                self.assertEqual(self.file_state(note), original_note)
                for identity in (baseline["id"], recovered["id"]):
                    self.assertIn(identity, summary.read_text(encoding="utf-8"))
                repaired = self.file_state(note, summary)
                self.run_cli(*arguments, root=root)
                self.assertEqual(self.file_state(note, summary), repaired)

    def test_retry_after_interrupted_restore_repairs_summary_without_rewriting_the_note(self):
        original = self.save("restorable", "Restorable fact", "Original conclusion.")
        self.forget(original)
        summary = self.root / "memory_summary.md"
        deleted_summary = summary.read_bytes()
        source = self.workspace / "restored.md"
        source.write_text("Restored conclusion.\n", encoding="utf-8")
        arguments = ("save", "--agent", "codex", "--key", "restorable", "--title", "Restorable fact",
                     "--global", "--restore", "--file", source)
        interrupted = self.gated_cli("rebuild_summary", *arguments)
        self.assertEqual(summary.read_bytes(), deleted_summary)
        interrupted.terminate()
        interrupted.communicate(timeout=5)
        self.assertLess(interrupted.returncode, 0)
        restored = self.run_cli("search", "Restored conclusion")[0]
        self.assertEqual(restored["id"], original["id"])
        note = Path(restored["path"])
        state = self.file_state(note)
        retried = self.run_cli(*arguments)
        self.assertEqual(retried["status"], "unchanged")
        self.assertEqual(self.file_state(note), state)
        self.assertIn(restored["id"], summary.read_text(encoding="utf-8"))
        repaired = self.file_state(note, summary)
        self.assertEqual(self.run_cli(*arguments)["status"], "unchanged")
        self.assertEqual(self.file_state(note, summary), repaired)

    def test_sync_is_idempotent_across_agents_and_records_agent_when_content_changes(self):
        source = self.workspace / "native.md"
        source.write_text("original-marker\n", encoding="utf-8")
        arguments = ("sync", "--source", source, "--global")
        self.assertEqual(self.run_cli(*arguments, "--agent", "codex"),
                         {"saved": 1, "unchanged": 0, "forgotten": 0})
        original = self.run_cli("search", "original-marker")[0]
        note = Path(original["path"])
        summary = self.root / "memory_summary.md"
        state = self.file_state(note, summary)
        for agent in ("claude-code", "codex"):
            with self.subTest(agent=agent):
                self.assertEqual(self.run_cli(*arguments, "--agent", agent),
                                 {"saved": 0, "unchanged": 1, "forgotten": 0})
                self.assertEqual(self.file_state(note, summary), state)
        source.write_text("changed-marker\n", encoding="utf-8")
        self.assertEqual(self.run_cli(*arguments, "--agent", "claude-code"),
                         {"saved": 1, "unchanged": 0, "forgotten": 0})
        updated = self.run_cli("search", "changed-marker")[0]
        self.assertEqual(updated["id"], original["id"])
        self.assertEqual(updated["agent"], "claude-code")
        self.assertNotEqual(self.file_state(note, summary), state)

    def test_invalid_input_does_not_overwrite_existing_note(self):
        saved = self.save("safe", "Valid title", "Keep this memory.")
        note = Path(saved["path"])
        original = note.read_bytes()
        arguments = ("save", "--agent", "codex", "--key", "safe", "--global")
        for title, body in [("Valid title", "  \n"), ("  ", "Replacement")]:
            with self.subTest(title=title, body=body):
                self.run_cli(*arguments, "--title", title, body=body, success=False)
                self.assertEqual(note.read_bytes(), original)
        self.run_cli(
            *arguments, "--title", "Valid title", "--file", self.workspace / "missing.md", success=False,
        )
        self.assertEqual(note.read_bytes(), original)
        self.run_cli("forget", "../safe", success=False)
        self.assertEqual(note.read_bytes(), original)

    def test_path_traversal_and_symlinks_are_rejected(self):
        self.run_cli(
            "save", "--agent", "codex", "--key", "../escape", "--title", "Unsafe", "--global",
            body="Do not write outside the store.", success=False,
        )
        native = self.workspace / "native"
        native.mkdir()
        source = native / "source.md"
        source.write_text("# Linked source\n\nDo not import through symlinks.\n", encoding="utf-8")
        file_link = self.workspace / "file-link.md"
        file_link.symlink_to(source)
        directory_link = self.workspace / "directory-link"
        directory_link.symlink_to(native, target_is_directory=True)
        for linked in (file_link, directory_link):
            with self.subTest(source=linked):
                self.run_cli("sync", "--agent", "codex", "--source", linked, "--global", success=False)
        self.root.mkdir(exist_ok=True)
        root_link = self.workspace / "root-link"
        root_link.symlink_to(self.root, target_is_directory=True)
        self.run_cli("search", "anything", root=root_link, success=False)
        for name in ("notes", "tombstones"):
            with self.subTest(directory=name):
                unsafe_root = self.workspace / f"unsafe-{name}"
                unsafe_root.mkdir()
                (unsafe_root / name).symlink_to(native, target_is_directory=True)
                self.run_cli("search", "anything", root=unsafe_root, success=False)

    def test_concurrent_saves_preserve_every_note_and_index_entry(self):
        def save_note(number):
            return self.save(f"parallel-{number}", f"Parallel note {number}", f"parallel-marker {number}")

        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            saved = list(executor.map(save_note, range(12)))
        self.assertEqual(len({item["id"] for item in saved}), 12)
        self.assertEqual(
            {item["id"] for item in self.run_cli("search", "parallel-marker")},
            {item["id"] for item in saved},
        )
        summary = (self.root / "memory_summary.md").read_text(encoding="utf-8")
        for number in range(12):
            self.assertIn(f"Parallel note {number}", summary)

    def test_sync_rejects_source_containing_or_inside_shared_root(self):
        saved = self.save("safe", "Preserved note", "Keep the original note.")
        original = Path(saved["path"]).read_bytes()
        nested = self.root / "native"
        nested.mkdir()
        (nested / "native.md").write_text("# Recursive import\n\nDo not import.\n", encoding="utf-8")
        for source in (self.root, nested, self.workspace):
            with self.subTest(source=source):
                self.run_cli("sync", "--agent", "codex", "--source", source, "--global", success=False)
                self.assertEqual(Path(saved["path"]).read_bytes(), original)
        self.assertEqual(len(list((self.root / "notes").glob("*.md"))), 1)


if __name__ == "__main__":
    unittest.main()
