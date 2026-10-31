"""Regression fixtures for repository checks; no network or installed skills."""

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.verify_repo import verify, verify_scripts


class VerifyRepoTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for path in ("README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE", "skills/README.md"):
            self.write(path, "# Example\n")
        self.write("VERSION", "0.1.0\n")

    def write(self, path, content):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def skill(self, metadata="name: example\ndescription: |\n  Use for example tasks."):
        self.write("skills/example/SKILL.md", "---\n" + metadata + "\n---\n# Instructions\n")
        self.write("skills/README.md", "| [example](./example/SKILL.md) | Example tasks |\n")

    def errors(self):
        return "\n".join(verify(self.root)[0])

    def test_empty_repository_is_valid(self):
        self.assertEqual(verify(self.root), ([], 0))

    def test_skill_with_multiline_description_is_valid(self):
        self.skill()
        self.assertEqual(verify(self.root), ([], 1))

    def test_repository_template_can_become_a_skill(self):
        template = Path(__file__).resolve().parents[1] / "assets/skill-template/SKILL.md.template"
        self.write("skills/example-skill/SKILL.md", template.read_text(encoding="utf-8"))
        self.write("skills/README.md", "| [example-skill](./example-skill/SKILL.md) | Example |\n")
        self.assertEqual(verify(self.root), ([], 1))

    def test_name_must_match_directory(self):
        self.skill("name: other\ndescription: Example")
        self.assertIn("name must match", self.errors())

    def test_invalid_name_and_description(self):
        self.skill("name: example--bad\ndescription: false")
        self.assertIn("name must match", self.errors())
        self.assertIn("description must be", self.errors())

    def test_duplicate_and_malformed_yaml(self):
        for metadata in ("name: example\nname: duplicate", "name: ["):
            with self.subTest(metadata=metadata):
                self.skill(metadata)
                self.assertIn("invalid YAML", self.errors())

    def test_missing_entrypoint_and_catalog_link(self):
        self.skill()
        self.write("skills/README.md", "# Skills\n")
        self.assertIn("missing link in", self.errors())
        (self.root / "skills/example/SKILL.md").unlink()
        self.assertIn("missing regular SKILL.md", self.errors())

    def test_missing_frontmatter_and_body(self):
        self.skill()
        self.write("skills/example/SKILL.md", "# No metadata\n")
        self.assertIn("missing YAML frontmatter", self.errors())
        self.write("skills/example/SKILL.md", "---\nname: example\ndescription: Example\n---\n")
        self.assertIn("missing instructions", self.errors())

    def test_broken_links_and_reference_targets(self):
        self.write("README.md", "[broken](missing.md)\n[reference][id]\n\n[id]: missing-too.md\n")
        self.assertIn("missing link target: missing.md", self.errors())
        self.assertIn("missing link target: missing-too.md", self.errors())

    def test_github_document_links_are_checked(self):
        self.write(".github/pull_request_template.md", "[missing](missing.md)\n")
        self.assertIn(".github/pull_request_template.md: missing link target", self.errors())

    def test_code_and_remote_links_are_ignored(self):
        self.write("README.md", "```md\n[example](missing.md)\n```\n"
                   "`[example](missing.md)`\n[external](https://example.com)\n[anchor](#example)\n")
        self.assertEqual(self.errors(), "")

    def test_encoded_link_and_fragment(self):
        self.write("a file.md", "# Target\n")
        self.write("README.md", "[target](a%20file.md#target)\n")
        self.assertEqual(self.errors(), "")

    def test_escape_and_symlink_targets_are_rejected(self):
        self.write("README.md", "[outside](../outside.md)\n")
        self.assertIn("link escapes repository", self.errors())
        (self.root / "escape").symlink_to(self.root.parent, target_is_directory=True)
        self.write("README.md", "[outside](escape/outside.md)\n")
        self.assertIn("link escapes repository", self.errors())

    def test_root_entrypoint_and_bad_version(self):
        self.write("SKILL.md", "# Root\n")
        self.write("VERSION", "v0.1.0\n")
        self.assertIn("root entrypoint", self.errors())
        self.assertIn("expected MAJOR.MINOR.PATCH", self.errors())

    def test_python_syntax_is_checked_without_execution(self):
        self.write("skills/example/scripts/example.py", "raise RuntimeError('must not execute')\n")
        self.assertEqual(verify_scripts(self.root), [])
        self.write("skills/example/scripts/example.py", "def broken(\n")
        self.assertEqual(len(verify_scripts(self.root)), 1)
        self.write(".venv/broken.py", "def broken(\n")
        (self.root / "skills/example/scripts/example.py").unlink()
        self.assertEqual(verify_scripts(self.root), [])

    def test_cli_fails_for_invalid_repository(self):
        script = Path(__file__).resolve().parents[1] / "scripts/verify_repo.py"
        self.write("VERSION", "not-a-version\n")
        result = subprocess.run([sys.executable, str(script), "--root", str(self.root)],
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn("VERSION", result.stderr)


if __name__ == "__main__":
    unittest.main()
