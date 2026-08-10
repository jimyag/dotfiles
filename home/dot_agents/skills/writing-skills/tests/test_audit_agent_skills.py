#!/usr/bin/env python3

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "audit_agent_skills.py"
SPEC = importlib.util.spec_from_file_location("audit_agent_skills", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


def write_skill(root: Path, name: str, frontmatter: str, body: str = "# Test\n") -> Path:
    skill = root / name
    skill.mkdir()
    (skill / "SKILL.md").write_text(
        f"---\n{frontmatter}\n---\n\n{body}", encoding="utf-8"
    )
    return skill


class AuditAgentSkillsTests(unittest.TestCase):
    def test_portable_minimal_skill_has_no_errors(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            write_skill(
                root,
                "sample-skill",
                "name: sample-skill\ndescription: Use this skill when testing a portable skill.",
            )
            _, findings = MODULE.audit(root, strict_portable=True, require_evals=False)
            self.assertFalse([item for item in findings if item.severity == "error"])

    def test_client_extension_is_error_only_in_portable_profile(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            write_skill(
                root,
                "sample-skill",
                "name: sample-skill\ndescription: Use this skill when testing.\nwhen_to_use: testing",
            )
            _, portable = MODULE.audit(root, strict_portable=True, require_evals=False)
            _, local = MODULE.audit(root, strict_portable=False, require_evals=False)
            self.assertEqual(
                [item.severity for item in portable if item.code == "client-extension-frontmatter"],
                ["error"],
            )
            self.assertEqual(
                [item.severity for item in local if item.code == "client-extension-frontmatter"],
                ["warning"],
            )

    def test_name_and_allowed_tools_rules(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            write_skill(
                root,
                "sample-skill",
                "name: other-name\ndescription: Use this skill when testing.\nallowed-tools:\n  - Read",
            )
            _, findings = MODULE.audit(root, strict_portable=True, require_evals=False)
            codes = {item.code for item in findings}
            self.assertIn("name-directory-mismatch", codes)
            self.assertIn("allowed-tools-not-string", codes)

    def test_broken_and_deep_references_are_reported(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            write_skill(
                root,
                "sample-skill",
                "name: sample-skill\ndescription: Use this skill when testing.",
                "# Test\n[missing](references/nested/missing.md)\n",
            )
            _, findings = MODULE.audit(root, strict_portable=True, require_evals=False)
            codes = {item.code for item in findings}
            self.assertIn("broken-reference", codes)
            self.assertIn("deep-reference", codes)

    def test_local_shared_reference_is_info_in_local_profile(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            skill = write_skill(
                root,
                "sample-skill",
                "name: sample-skill\ndescription: Use this skill when testing.",
                "# Test\n[shared](../_shared/rules.md)\n",
            )
            shared = root / "_shared"
            shared.mkdir()
            (shared / "rules.md").write_text("# Rules\n", encoding="utf-8")
            _, portable = MODULE.audit(root, strict_portable=True, require_evals=False)
            _, local = MODULE.audit(root, strict_portable=False, require_evals=False)
            self.assertEqual(
                [item.severity for item in portable if item.code == "reference-outside-skill"],
                ["warning"],
            )
            self.assertEqual(
                [item.severity for item in local if item.code == "local-shared-reference"],
                ["info"],
            )

    def test_python_dependency_and_interactive_input_are_reported(self):
        with tempfile.TemporaryDirectory() as name:
            root = Path(name)
            skill = write_skill(
                root,
                "sample-skill",
                "name: sample-skill\ndescription: Use this skill when testing.",
                "# Test\nRun `scripts/run.py`.\n",
            )
            scripts = skill / "scripts"
            scripts.mkdir()
            (scripts / "run.py").write_text(
                "import requests\nvalue = input('value: ')\n", encoding="utf-8"
            )
            _, findings = MODULE.audit(root, strict_portable=True, require_evals=False)
            codes = {item.code for item in findings}
            self.assertIn("python-dependencies-not-declared", codes)
            self.assertIn("interactive-script", codes)
            self.assertIn("script-help-not-detected", codes)


if __name__ == "__main__":
    unittest.main()
