#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "pyyaml>=6.0,<7",
# ]
# ///
"""Audit Agent Skills for specification compliance and maintainability risks."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml


OFFICIAL_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK_PATTERN = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
SCRIPT_PATH_PATTERN = re.compile(r"(?:^|[\s`'\"])(scripts/[A-Za-z0-9_./-]+)")
WHEN_MARKERS = (
    "use when",
    "use this skill when",
    "when the user",
    "时使用",
    "适用于",
    "仅当",
)
CONTENTS_PATTERN = re.compile(
    r"^##\s+(contents|table of contents|目录)\s*$", re.IGNORECASE | re.MULTILINE
)
INTERACTIVE_PATTERNS = (
    re.compile(r"\binput\s*\("),
    re.compile(r"\bread\s+-p\b"),
    re.compile(r"\bselect\s+\w+\s+in\b"),
)
VERSION_BOUND_PATTERN = re.compile(r"(?:==|~=|<|===)")


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    skill: str
    path: str
    message: str


def finding(
    severity: str, code: str, skill: str, path: Path, message: str
) -> Finding:
    return Finding(severity, code, skill, str(path), message)


def split_frontmatter(path: Path) -> tuple[dict[str, Any] | None, str, list[Finding]]:
    skill = path.parent.name
    findings: list[Finding] = []
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return None, "", [finding("error", "unreadable-skill", skill, path, str(exc))]

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, text, [
            finding(
                "error",
                "missing-frontmatter",
                skill,
                path,
                "SKILL.md must start with YAML frontmatter delimited by ---.",
            )
        ]
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration:
        return None, text, [
            finding(
                "error",
                "unterminated-frontmatter",
                skill,
                path,
                "SKILL.md frontmatter has no closing --- delimiter.",
            )
        ]

    try:
        parsed = yaml.safe_load("\n".join(lines[1:end])) or {}
    except yaml.YAMLError as exc:
        return None, text, [
            finding("error", "invalid-frontmatter-yaml", skill, path, str(exc))
        ]
    if not isinstance(parsed, dict):
        return None, text, [
            finding(
                "error",
                "frontmatter-not-map",
                skill,
                path,
                "SKILL.md frontmatter must be a YAML mapping.",
            )
        ]
    return parsed, "\n".join(lines[end + 1 :]), findings


def check_frontmatter(
    skill_dir: Path, frontmatter: dict[str, Any], strict_portable: bool
) -> list[Finding]:
    skill = skill_dir.name
    path = skill_dir / "SKILL.md"
    findings: list[Finding] = []

    name = frontmatter.get("name")
    if not isinstance(name, str) or not name:
        findings.append(
            finding("error", "invalid-name", skill, path, "name must be a non-empty string.")
        )
    else:
        if len(name) > 64 or not NAME_PATTERN.fullmatch(name):
            findings.append(
                finding(
                    "error",
                    "invalid-name",
                    skill,
                    path,
                    "name must be 1-64 lowercase ASCII letters, numbers, or single hyphens.",
                )
            )
        if name != skill:
            findings.append(
                finding(
                    "error",
                    "name-directory-mismatch",
                    skill,
                    path,
                    f"name {name!r} must match directory {skill!r}.",
                )
            )

    description = frontmatter.get("description")
    if not isinstance(description, str) or not description.strip():
        findings.append(
            finding(
                "error",
                "invalid-description",
                skill,
                path,
                "description must be a non-empty string.",
            )
        )
    else:
        if len(description) > 1024:
            findings.append(
                finding(
                    "error",
                    "description-too-long",
                    skill,
                    path,
                    f"description has {len(description)} characters; maximum is 1024.",
                )
            )
        lowered = description.lower()
        if not any(marker in lowered for marker in WHEN_MARKERS):
            findings.append(
                finding(
                    "warning",
                    "description-missing-trigger-language",
                    skill,
                    path,
                    "description should state when to use the skill in user-intent language.",
                )
            )

    for key, maximum in (("license", None), ("compatibility", 500)):
        value = frontmatter.get(key)
        if value is None:
            continue
        if not isinstance(value, str) or not value.strip():
            findings.append(
                finding("error", f"invalid-{key}", skill, path, f"{key} must be a non-empty string.")
            )
        elif maximum is not None and len(value) > maximum:
            findings.append(
                finding(
                    "error",
                    f"{key}-too-long",
                    skill,
                    path,
                    f"{key} has {len(value)} characters; maximum is {maximum}.",
                )
            )

    metadata = frontmatter.get("metadata")
    if metadata is not None:
        if not isinstance(metadata, dict):
            findings.append(
                finding("error", "invalid-metadata", skill, path, "metadata must be a mapping.")
            )
        else:
            bad_entries = [
                str(key)
                for key, value in metadata.items()
                if not isinstance(key, str) or not isinstance(value, str)
            ]
            if bad_entries:
                findings.append(
                    finding(
                        "error",
                        "invalid-metadata-value",
                        skill,
                        path,
                        "metadata keys and values must be strings: " + ", ".join(bad_entries),
                    )
                )

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        findings.append(
            finding(
                "error" if strict_portable else "warning",
                "allowed-tools-not-string",
                skill,
                path,
                "Agent Skills specifies allowed-tools as one space-separated string.",
            )
        )

    unexpected = sorted(set(frontmatter) - OFFICIAL_FIELDS)
    if unexpected:
        findings.append(
            finding(
                "error" if strict_portable else "warning",
                "client-extension-frontmatter",
                skill,
                path,
                "Non-standard top-level fields: " + ", ".join(unexpected),
            )
        )
    return findings


def local_markdown_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip().split("#", 1)[0]
    if not target or target.startswith(("http://", "https://", "mailto:", "#")):
        return None
    target = target.strip("<>")
    return (source.parent / target).resolve()


def check_links(
    skill_dir: Path, body: str, strict_portable: bool
) -> list[Finding]:
    skill = skill_dir.name
    skill_file = skill_dir / "SKILL.md"
    findings: list[Finding] = []
    root = skill_dir.resolve()
    for raw_target in MARKDOWN_LINK_PATTERN.findall(body):
        target = local_markdown_target(skill_file, raw_target)
        if target is None:
            continue
        try:
            relative = target.relative_to(root)
        except ValueError:
            is_local_shared = raw_target.startswith("../_shared/")
            findings.append(
                finding(
                    "warning" if strict_portable or not is_local_shared else "info",
                    (
                        "reference-outside-skill"
                        if strict_portable or not is_local_shared
                        else "local-shared-reference"
                    ),
                    skill,
                    skill_file,
                    (
                        f"Reference leaves the skill root: {raw_target}"
                        if strict_portable or not is_local_shared
                        else f"Documented local shared reference: {raw_target}"
                    ),
                )
            )
            continue
        if not target.exists():
            findings.append(
                finding(
                    "error",
                    "broken-reference",
                    skill,
                    skill_file,
                    f"Referenced path does not exist: {raw_target}",
                )
            )
        if len(relative.parts) > 2:
            findings.append(
                finding(
                    "warning",
                    "deep-reference",
                    skill,
                    skill_file,
                    f"Reference is more than one directory deep: {raw_target}",
                )
            )
    return findings


def python_imports(path: Path) -> set[str]:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError):
        return set()
    imports: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".", 1)[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".", 1)[0])
    return imports


def pep723_dependencies(text: str) -> list[str] | None:
    match = re.search(r"(?ms)^# /// script\s*$\n(.*?)^# ///\s*$", text)
    if not match:
        return None
    block_lines = []
    for line in match.group(1).splitlines():
        block_lines.append(re.sub(r"^# ?", "", line))
    try:
        import tomllib

        parsed = tomllib.loads("\n".join(block_lines))
    except (ValueError, TypeError):
        return []
    dependencies = parsed.get("dependencies", [])
    return dependencies if isinstance(dependencies, list) else []


def check_scripts(skill_dir: Path, body: str) -> list[Finding]:
    skill = skill_dir.name
    findings: list[Finding] = []
    scripts_dir = skill_dir / "scripts"
    if not scripts_dir.is_dir():
        return findings

    referenced = {match.rstrip(".,;:)") for match in SCRIPT_PATH_PATTERN.findall(body)}
    local_modules = {path.stem for path in scripts_dir.glob("*.py")}
    # Chezmoi strips executable_ from target filenames, so source imports use the
    # target module name (for example executable_camofox_client.py -> camofox_client.py).
    local_modules.update(name.removeprefix("executable_") for name in tuple(local_modules))
    local_modules.add("scripts")
    for path in sorted(scripts_dir.rglob("*")):
        if not path.is_file() or path.suffix not in {".py", ".sh", ".js", ".ts", ".rb"}:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            continue
        relative = path.relative_to(skill_dir).as_posix()
        is_entrypoint = relative in referenced

        if is_entrypoint and not re.search(
            r"--help|ArgumentParser|click\.command|typer\.|Usage:|usage\(", text
        ):
            findings.append(
                finding(
                    "warning",
                    "script-help-not-detected",
                    skill,
                    path,
                    "Referenced script has no detectable --help interface.",
                )
            )
        if any(pattern.search(text) for pattern in INTERACTIVE_PATTERNS):
            findings.append(
                finding(
                    "error",
                    "interactive-script",
                    skill,
                    path,
                    "Scripts used by agents must not block on interactive input.",
                )
            )

        if path.suffix == ".py":
            dependencies = pep723_dependencies(text)
            imports = python_imports(path)
            third_party = sorted(
                imports - set(sys.stdlib_module_names) - local_modules - {"__future__"}
            )
            if third_party and dependencies is None:
                findings.append(
                    finding(
                        "warning",
                        "python-dependencies-not-declared",
                        skill,
                        path,
                        "Third-party imports lack PEP 723 metadata: " + ", ".join(third_party),
                    )
                )
            if dependencies:
                unbounded = [
                    dependency
                    for dependency in dependencies
                    if isinstance(dependency, str) and not VERSION_BOUND_PATTERN.search(dependency)
                ]
                if unbounded:
                    findings.append(
                        finding(
                            "warning",
                            "python-dependency-not-bounded",
                            skill,
                            path,
                            "Add an upper bound, compatible release, or exact pin: "
                            + ", ".join(unbounded),
                        )
                    )
    return findings


def check_structure(skill_dir: Path, body: str, require_evals: bool) -> list[Finding]:
    skill = skill_dir.name
    path = skill_dir / "SKILL.md"
    findings: list[Finding] = []
    line_count = len(path.read_text(encoding="utf-8").splitlines())
    if line_count > 500:
        findings.append(
            finding(
                "warning",
                "skill-md-over-500-lines",
                skill,
                path,
                f"SKILL.md has {line_count} lines; progressive disclosure recommends under 500.",
            )
        )
    if len(body) > 20_000:
        findings.append(
            finding(
                "warning",
                "skill-md-context-heavy",
                skill,
                path,
                f"SKILL.md body has {len(body)} characters; review against the 5,000-token guidance.",
            )
        )

    if require_evals and not (skill_dir / "evals" / "evals.json").is_file():
        findings.append(
            finding(
                "warning",
                "missing-output-evals",
                skill,
                skill_dir,
                "No evals/evals.json found for structured output-quality evaluation.",
            )
        )

    for reference_dir_name in ("reference", "references"):
        reference_dir = skill_dir / reference_dir_name
        if not reference_dir.is_dir():
            continue
        for reference in reference_dir.rglob("*.md"):
            try:
                text = reference.read_text(encoding="utf-8")
            except (OSError, UnicodeError):
                continue
            lines = len(text.splitlines())
            if lines > 100 and not CONTENTS_PATTERN.search(text):
                findings.append(
                    finding(
                        "warning",
                        "long-reference-without-contents",
                        skill,
                        reference,
                        f"Reference has {lines} lines and no Contents/目录 section.",
                    )
                )
    return findings


def discover_skill_dirs(root: Path) -> list[Path]:
    if (root / "SKILL.md").is_file():
        return [root]
    return sorted(
        child for child in root.iterdir() if child.is_dir() and (child / "SKILL.md").is_file()
    )


def audit(
    root: Path, strict_portable: bool, require_evals: bool
) -> tuple[list[Path], list[Finding]]:
    skill_dirs = discover_skill_dirs(root)
    findings: list[Finding] = []
    for skill_dir in skill_dirs:
        frontmatter, body, parse_findings = split_frontmatter(skill_dir / "SKILL.md")
        findings.extend(parse_findings)
        if frontmatter is None:
            continue
        findings.extend(check_frontmatter(skill_dir, frontmatter, strict_portable))
        findings.extend(check_links(skill_dir, body, strict_portable))
        findings.extend(check_scripts(skill_dir, body))
        findings.extend(check_structure(skill_dir, body, require_evals))
    return skill_dirs, findings


def summary(skill_dirs: Iterable[Path], findings: Iterable[Finding]) -> dict[str, Any]:
    skill_list = list(skill_dirs)
    finding_list = list(findings)
    severity_counts = Counter(item.severity for item in finding_list)
    code_counts = Counter(item.code for item in finding_list)
    affected = sorted({item.skill for item in finding_list})
    return {
        "skills_scanned": len(skill_list),
        "skills_with_findings": len(affected),
        "severity_counts": dict(sorted(severity_counts.items())),
        "code_counts": dict(sorted(code_counts.items())),
    }


def render_text(report: dict[str, Any]) -> None:
    stats = report["summary"]
    print(
        f"skills={stats['skills_scanned']} affected={stats['skills_with_findings']} "
        f"errors={stats['severity_counts'].get('error', 0)} "
        f"warnings={stats['severity_counts'].get('warning', 0)}"
    )
    for item in report["findings"]:
        print(
            f"{item['severity'].upper()} {item['code']} "
            f"{item['skill']} {item['path']}: {item['message']}"
        )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Audit one Agent Skill or a directory of skills against agentskills.io rules."
    )
    parser.add_argument("root", type=Path, help="skill directory or parent directory of skills")
    parser.add_argument(
        "--profile",
        choices=("portable", "local"),
        default="portable",
        help="portable treats client-only frontmatter as errors; local reports warnings (default: portable)",
    )
    parser.add_argument(
        "--format", choices=("text", "json"), default="text", help="output format"
    )
    parser.add_argument(
        "--require-evals",
        action="store_true",
        help="warn when evals/evals.json is missing",
    )
    parser.add_argument(
        "--fail-on",
        choices=("error", "warning", "never"),
        default="error",
        help="exit non-zero for the selected severity threshold (default: error)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    root = args.root.expanduser().resolve()
    if not root.is_dir():
        print(f"Error: skill root is not a directory: {root}", file=sys.stderr)
        return 2
    try:
        skill_dirs, findings = audit(
            root, strict_portable=args.profile == "portable", require_evals=args.require_evals
        )
    except OSError as exc:
        print(f"Error: failed to scan {root}: {exc}", file=sys.stderr)
        return 2
    if not skill_dirs:
        print(f"Error: no SKILL.md files found under: {root}", file=sys.stderr)
        return 2

    report = {
        "root": str(root),
        "profile": args.profile,
        "summary": summary(skill_dirs, findings),
        "findings": [asdict(item) for item in findings],
    }
    if args.format == "json":
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        render_text(report)

    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning" and any(
        item.severity in {"error", "warning"} for item in findings
    ):
        return 1
    if args.fail_on == "error" and any(item.severity == "error" for item in findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
