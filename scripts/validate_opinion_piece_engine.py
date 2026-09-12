#!/usr/bin/env python3
"""Repository checks for the opinion-piece-engine package."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


SEMVER = re.compile(r"^\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
SECRET_PATTERNS = {
    "GitHub token": re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    "OpenAI-style key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}"),
    "private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}
FORBIDDEN_RUNTIME_NAMES = {
    "README.md",
    "CHANGELOG.md",
    "INSTALLATION_GUIDE.md",
    "QUICK_REFERENCE.md",
}
ALLOWED_AGENT_KEYS = {"display_name", "short_description", "default_prompt", "icon_small", "icon_large"}


def load_json(path: Path, errors: list[str]):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        errors.append(f"invalid JSON: {path}: {exc}")
        return None


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        errors.append(f"missing opening frontmatter delimiter: {path}")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"missing closing frontmatter delimiter: {path}")
        return {}
    values: dict[str, str] = {}
    for line in lines[1:end]:
        if not line.strip():
            continue
        if ":" not in line:
            errors.append(f"malformed frontmatter line in {path}: {line!r}")
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    if set(values) != {"name", "description"}:
        errors.append(f"frontmatter keys must be exactly name, description: {path}")
    if values.get("name") != "opinion-piece-engine":
        errors.append(f"frontmatter name must be opinion-piece-engine: {path}")
    return values


def parse_simple_openai_yaml(path: Path, errors: list[str]) -> None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "interface:":
        errors.append(f"agents/openai.yaml must contain only an interface mapping: {path}")
        return
    keys: set[str] = set()
    for line in lines[1:]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        match = re.fullmatch(r"  ([a-z_]+):\s*(.+)", line)
        if not match:
            errors.append(f"unsupported YAML structure in {path}: {line!r}")
            continue
        key, value = match.groups()
        keys.add(key)
        if key not in ALLOWED_AGENT_KEYS:
            errors.append(f"unsupported agents/openai.yaml key {key!r}: {path}")
        if len(value) < 2 or value[0] != '"' or value[-1] != '"':
            errors.append(f"agents/openai.yaml string must be double-quoted: {key}")
    required = {"display_name", "short_description", "default_prompt"}
    if not required.issubset(keys):
        errors.append(f"agents/openai.yaml missing keys: {sorted(required - keys)}")


def check_markdown_links(repo: Path, errors: list[str]) -> None:
    for path in repo.rglob("*.md"):
        text = path.read_text(encoding="utf-8", errors="replace")
        for target in MARKDOWN_LINK.findall(text):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            clean = target.split("#", 1)[0]
            if clean and not (path.parent / clean).resolve().exists():
                errors.append(f"broken relative Markdown link in {path}: {target}")


def check_schemas(repo: Path, errors: list[str], engine_version: str | None = None) -> None:
    for name in ("input.schema.json", "output.schema.json"):
        path = repo / "schemas" / "opinion-piece-engine" / name
        data = load_json(path, errors) if path.exists() else None
        if data is None:
            if not path.exists():
                errors.append(f"missing schema: {path}")
            continue
        if data.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
            errors.append(f"schema must use JSON Schema 2020-12: {path}")
        if data.get("type") != "object" or not data.get("required"):
            errors.append(f"schema requires an object root and required fields: {path}")
    examples = {
        "minimal-input.json": {"schema_version", "mode", "request"},
        "minimal-output.json": {"schema_version", "engine", "engine_version", "mode", "release_status", "assumptions", "artifacts"},
    }
    for name, required in examples.items():
        path = repo / "schemas" / "opinion-piece-engine" / "examples" / name
        data = load_json(path, errors) if path.exists() else None
        if data is None:
            if not path.exists():
                errors.append(f"missing schema example: {path}")
            continue
        missing = required - set(data)
        if missing:
            errors.append(f"schema example missing {sorted(missing)}: {path}")
        if name == "minimal-output.json" and engine_version and data.get("engine_version") != engine_version:
            errors.append(f"output example engine_version must match VERSION: {path}")


def check_cases(repo: Path, errors: list[str]) -> None:
    path = repo / "tests" / "opinion-piece-engine" / "cases" / "cases.json"
    data = load_json(path, errors) if path.exists() else None
    if data is None:
        if not path.exists():
            errors.append(f"missing evaluation cases: {path}")
        return
    cases = data.get("cases")
    if not isinstance(cases, list) or not cases:
        errors.append(f"evaluation suite has no cases: {path}")
        return
    seen: set[str] = set()
    required = {"id", "mode", "prompt", "positive_assertions", "negative_assertions"}
    for case in cases:
        missing = required - set(case)
        if missing:
            errors.append(f"case missing {sorted(missing)}: {case.get('id', '<unknown>')}")
        case_id = case.get("id")
        if case_id in seen:
            errors.append(f"duplicate case id: {case_id}")
        seen.add(case_id)
        if not case.get("positive_assertions") or not case.get("negative_assertions"):
            errors.append(f"case needs positive and negative assertions: {case_id}")
        for fixture in case.get("fixture_paths", []):
            if not (repo / fixture).is_file():
                errors.append(f"missing fixture for {case_id}: {fixture}")


def check_tree(repo: Path, errors: list[str]) -> None:
    skill = repo
    required = [repo / "SKILL.md", repo / "VERSION", repo / "agents" / "openai.yaml"]
    for path in required:
        if not path.is_file():
            errors.append(f"missing required file: {path}")
    for path in repo.rglob("*"):
        if path.is_symlink():
            errors.append(f"symlinks are forbidden: {path}")
        if path.is_file() and path.name in FORBIDDEN_RUNTIME_NAMES and skill in path.parents:
            errors.append(f"forbidden runtime documentation file: {path}")
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        internal_root = "/root/" + ".codex/"
        internal_skill = re.compile("skill-" + r"[0-9a-f]{16,}")
        if internal_root in text or internal_skill.search(text):
            errors.append(f"internal installation path or ID found: {path}")
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(text):
                errors.append(f"possible {label} found: {path}")


def validate(repo: Path) -> list[str]:
    errors: list[str] = []
    skill = repo
    check_tree(repo, errors)
    skill_md = skill / "SKILL.md"
    if skill_md.exists():
        parse_frontmatter(skill_md, errors)
    version_path = skill / "VERSION"
    if version_path.exists() and not SEMVER.fullmatch(version_path.read_text(encoding="utf-8").strip()):
        errors.append(f"VERSION is not semantic versioning: {version_path}")
    agent_path = skill / "agents" / "openai.yaml"
    if agent_path.exists():
        parse_simple_openai_yaml(agent_path, errors)
    check_markdown_links(repo, errors)
    engine_version = version_path.read_text(encoding="utf-8").strip() if version_path.exists() else None
    check_schemas(repo, errors, engine_version)
    check_cases(repo, errors)
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("repo", nargs="?", default=".")
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    errors = validate(repo)
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print("Opinion-piece engine repository validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
