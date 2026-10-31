"""Check Fenix source metadata and local Markdown link targets."""

import argparse
import os
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

import yaml


NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
VERSION = re.compile(r"(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)\.(?:0|[1-9]\d*)")
EXCLUDED = {".git", ".venv", "node_modules", "__pycache__", ".cache", "dist", "build"}
LINK = re.compile(r"!?\[[^\]\n]*\]\(\s*(<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")
REFERENCE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(<[^>]+>|\S+)", re.MULTILINE)


class UniqueLoader(yaml.SafeLoader):
    """Reject duplicate mapping keys instead of silently taking the last value."""


def unique_mapping(loader, node):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node)
        if key in mapping:
            raise ValueError("duplicate YAML key: {}".format(key))
        mapping[key] = loader.construct_object(value_node)
    return mapping


UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping)


def source_files(root):
    for directory, folders, files in os.walk(root, followlinks=False):
        folders[:] = sorted(folder for folder in folders
                            if folder not in EXCLUDED
                            and (not folder.startswith(".") or folder == ".github"))
        for name in sorted(files):
            path = Path(directory) / name
            if not path.is_symlink():
                yield path


def prose(text):
    """Omit fenced examples and inline code from link checks."""
    lines = []
    fence = None
    for line in text.splitlines():
        match = re.match(r"^\s{0,3}(`{3,}|~{3,})", line)
        if match:
            marker = match.group(1)
            if fence is None:
                fence = marker
            elif marker[0] == fence[0] and len(marker) >= len(fence):
                fence = None
            continue
        if fence is None:
            lines.append(line)
    return re.sub(r"(`+).*?\1", "", "\n".join(lines))


def link_targets(text):
    content = prose(text)
    return [match.group(1).strip("<>") for pattern in (LINK, REFERENCE)
            for match in pattern.finditer(content)]


def verify(root):
    root = root.resolve()
    errors = []
    for name in ("README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "VERSION", "skills/README.md"):
        if not (root / name).is_file():
            errors.append("missing required file: " + name)
    version = root / "VERSION"
    if version.is_file() and not VERSION.fullmatch(version.read_text(encoding="utf-8").strip()):
        errors.append("VERSION: expected MAJOR.MINOR.PATCH without a v prefix")
    if (root / "SKILL.md").exists():
        errors.append("SKILL.md: root entrypoint would hide nested skills; use skills/<name>/SKILL.md")

    catalog_path = root / "skills/README.md"
    catalog = link_targets(catalog_path.read_text(encoding="utf-8")) if catalog_path.is_file() else []
    catalog_files = {(catalog_path.parent / unquote(urlsplit(target).path)).resolve()
                     for target in catalog if not urlsplit(target).scheme}
    skill_count = 0
    skills = root / "skills"
    for folder in sorted(skills.iterdir()) if skills.is_dir() else []:
        if not folder.is_dir() or folder.name.startswith("."):
            continue
        if folder.is_symlink():
            errors.append("skills/{}: symlinked skills are not supported".format(folder.name))
            continue
        entry = folder / "SKILL.md"
        label = str(entry.relative_to(root))
        if not entry.is_file() or entry.is_symlink():
            errors.append(label + ": missing regular SKILL.md")
            continue
        skill_count += 1
        text = entry.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)\Z", text, re.DOTALL)
        if not match:
            errors.append(label + ": missing YAML frontmatter")
            continue
        try:
            data = yaml.load(match.group(1), Loader=UniqueLoader)
            if not isinstance(data, dict):
                raise ValueError("frontmatter must be a mapping")
        except (yaml.YAMLError, ValueError, TypeError) as exc:
            errors.append(label + ": invalid YAML: " + str(exc))
            continue
        name = data.get("name")
        if not isinstance(name, str) or not NAME.fullmatch(name) or len(name) > 64 or name != folder.name:
            errors.append(label + ": name must match the directory and use 1–64 lowercase letters, digits or single hyphens")
        description = data.get("description")
        if not isinstance(description, str) or not description.strip() or len(description) > 1024:
            errors.append(label + ": description must be a non-empty string of at most 1024 characters")
        if not match.group(2).strip():
            errors.append(label + ": missing instructions after frontmatter")
        if entry.resolve() not in catalog_files:
            errors.append(label + ": missing link in skills/README.md")

    for path in source_files(root):
        if path.suffix.lower() != ".md":
            continue
        for target in link_targets(path.read_text(encoding="utf-8")):
            parsed = urlsplit(target)
            if parsed.scheme or target.startswith("//") or not parsed.path:
                continue
            destination = (path.parent / unquote(parsed.path)).resolve()
            if root not in destination.parents and destination != root:
                errors.append("{}: link escapes repository: {}".format(path.relative_to(root), target))
            elif not destination.exists():
                errors.append("{}: missing link target: {}".format(path.relative_to(root), target))
    return errors, skill_count


def verify_scripts(root):
    errors = []
    for path in source_files(root):
        if path.suffix == ".py":
            try:
                compile(path.read_bytes(), str(path), "exec")
            except SyntaxError as exc:
                errors.append("{}: {}".format(path.relative_to(root), exc))
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--scripts-only", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.scripts_only:
        errors = verify_scripts(root)
        success = "Python syntax: OK (scripts were not executed)"
    else:
        errors, count = verify(root)
        success = "Repository: OK ({} skills; metadata and local link targets checked)".format(count)
    for error in errors:
        print("ERROR: " + error, file=sys.stderr)
    if errors:
        return 1
    print(success)
    return 0


if __name__ == "__main__":
    sys.exit(main())
