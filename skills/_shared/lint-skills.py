#!/usr/bin/env python3

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parent.parent
REQUIRED_FRONTMATTER = ("name:", "description:")


def check_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        return errors

    text = skill_file.read_text(encoding="utf-8")
    lines = text.splitlines()

    if not lines or lines[0].strip() != "---":
        errors.append(f"{skill_dir.name}: missing frontmatter start")
        return errors

    try:
        end = lines[1:].index("---") + 1
    except ValueError:
        errors.append(f"{skill_dir.name}: missing frontmatter end")
        return errors

    frontmatter = lines[1:end]
    for field in REQUIRED_FRONTMATTER:
        if not any(line.startswith(field) for line in frontmatter):
            errors.append(f"{skill_dir.name}: missing frontmatter field {field[:-1]}")

    body = "\n".join(lines[end + 1 :])
    if not any(line.startswith("# ") for line in lines[end + 1 :]):
        errors.append(f"{skill_dir.name}: missing top-level heading")

    if skill_dir.name in {"ci-analyze", "git-commit", "gh-view", "requesting-code-review"}:
        if "common-acceptance.md" not in body:
            errors.append(f"{skill_dir.name}: missing shared acceptance reference")

    return errors


def main() -> int:
    errors: list[str] = []
    for skill_dir in sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith(".")):
        if skill_dir.name == "_shared":
            continue
        errors.extend(check_skill(skill_dir))

    if errors:
        print("skill lint failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("skill lint passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
