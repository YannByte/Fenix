"""Verify the repository harness with isolated sources and synthetic Git state."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.harness import (ROOT, HarnessError, checkout_scope, install_local,
                             run_command, verification_plan, verify_scope)


class HarnessTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="fenix-harness-")
        self.addCleanup(self.temp.cleanup)
        self.scratch = Path(self.temp.name).resolve()
        self.source = self.scratch / "repo"
        self.source.mkdir()
        self.destination = self.scratch / "installed"

    def fixture(self):
        for name in ("README.md", "AGENTS.md", "CONTRIBUTING.md", "LICENSE"):
            (self.source / name).write_text("# Fixture\n")
        (self.source / "VERSION").write_text("0.1.0\n")
        catalog = []
        for name in ("fenix-alpha", "fenix-beta"):
            folder = self.source / "skills" / name
            folder.mkdir(parents=True)
            (folder / "SKILL.md").write_text(
                "---\nname: {}\ndescription: Synthetic task.\n---\n# Instructions\n".format(name))
            (folder / "LICENSE").write_text("Fixture license\n")
            catalog.append("[{}](./{}/SKILL.md)".format(name, name))
        (self.source / "skills/README.md").write_text("\n".join(catalog))
        private = self.source / ".agents/skills/fenix-private"
        private.mkdir(parents=True)
        (private / "SKILL.md").write_text(
            "---\nname: fenix-private\ndescription: Project workflow.\n---\n# Instructions\n")

    def test_inventory_preserves_names_staging_and_git_state(self):
        def git(*args):
            return run_command(["git", *args], self.source)

        git("init", "-q")
        for name in ("before name.md", "gone.md", "partial.md"):
            (self.source / name).write_text("one\n")
        git("add", ".")
        git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.com",
            "-c", "commit.gpgsign=false", "commit", "-qm", "fixture")
        renamed = "after\tname\n.md"
        git("mv", "before name.md", renamed)
        (self.source / "gone.md").unlink()
        (self.source / "partial.md").write_text("two\n")
        git("add", "partial.md")
        (self.source / "partial.md").write_text("three\n")
        untracked = "new\tfile\n.md"
        (self.source / untracked).write_text("untracked")
        before = git("status", "--porcelain=v1", "-z")
        index = (self.source / ".git/index").read_bytes()
        result = checkout_scope(self.source)
        changes = {item["path"]: item for item in result["changes"]}
        self.assertEqual(changes[renamed]["previous_path"], "before name.md")
        self.assertEqual(changes["partial.md"]["status"], "MM")
        self.assertEqual(changes["gone.md"]["status"], " D")
        self.assertEqual(changes[untracked]["status"], "??")
        self.assertEqual(len(changes), 4)
        self.assertEqual(git("status", "--porcelain=v1", "-z"), before)
        self.assertEqual((self.source / ".git/index").read_bytes(), index)

    def test_cli_resolves_its_repository_from_foreign_working_directory(self):
        output = run_command([sys.executable, str(ROOT / "scripts/harness.py"), "scope"], self.scratch)
        self.assertEqual(Path(json.loads(output)["root"]), ROOT)

    def test_verification_stops_at_failure_and_reports_completed_stages(self):
        calls = []

        def runner(command, root):
            calls.append(command[1])
            self.assertEqual(root, self.source)
            if command[1] == "verify-scripts":
                raise HarnessError("synthetic failure")
            return "passed\n"

        with contextlib.redirect_stdout(io.StringIO()):
            with self.assertRaisesRegex(HarnessError, "Stopped at verify-scripts; completed: verify-docs"):
                verify_scope("full", self.source, runner)
        self.assertEqual(calls, ["verify-docs", "verify-scripts"])

    def test_invalid_scope_executes_nothing(self):
        calls = []
        with self.assertRaises(HarnessError):
            verify_scope("unknown", self.source, lambda *args: calls.append(args))
        self.assertFalse(calls)
        self.assertEqual(len(verification_plan("repository")), 2)
        self.assertEqual(len(verification_plan("full")), 3)

    def test_commands_reject_failure_timeout_and_excess_output(self):
        cases = [(["-c", "raise SystemExit(7)"], {}, "exit 7"),
                 (["-c", "import time; time.sleep(5)"], {"timeout": 0.05}, "timeout"),
                 (["-c", "print('x' * 5000)"], {"output_limit": 100}, "output limit")]
        for args, options, expected in cases:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(HarnessError, expected):
                    run_command([sys.executable, *args], self.scratch, **options)

    @unittest.skipUnless(os.name == "posix", "Process-group cleanup is a POSIX contract")
    def test_timeout_stops_descendants(self):
        marker = self.scratch / "unexpected"
        child = "import time; from pathlib import Path; time.sleep(.4); Path({!r}).write_text('bad')".format(str(marker))
        parent = "import subprocess,sys,time; subprocess.Popen([sys.executable,'-c', {!r}]); time.sleep(5)".format(child)
        with self.assertRaisesRegex(HarnessError, "timeout"):
            run_command([sys.executable, "-c", parent], self.scratch, timeout=0.15)
        time.sleep(0.5)
        self.assertFalse(marker.exists())

    @unittest.skipUnless(os.name == "posix", "Process-group cleanup is a POSIX contract")
    def test_success_does_not_leave_background_descendants(self):
        marker = self.scratch / "unexpected-background"
        child = "import time; from pathlib import Path; time.sleep(.4); Path({!r}).write_text('bad')".format(str(marker))
        parent = "import subprocess,sys; subprocess.Popen([sys.executable,'-c', {!r}])".format(child)
        run_command([sys.executable, "-c", parent], self.scratch)
        time.sleep(0.5)
        self.assertFalse(marker.exists())

    def test_cli_installs_real_public_skills_in_isolation(self):
        destination = self.scratch / "local skills"
        command = [sys.executable, str(ROOT / "scripts/harness.py"),
                   "install", "--dest", str(destination), "--apply"]
        first = json.loads(run_command(command, self.scratch))
        names = sorted(p.name for p in (ROOT / "skills").iterdir() if (p / "SKILL.md").is_file())
        self.assertEqual([item["name"] for item in first["skills"]], names)
        self.assertTrue(first["applied"])
        for name in names:
            self.assertEqual((destination / name).resolve(), ROOT / "skills" / name)
            self.assertTrue((destination / name / "LICENSE").is_file())
        second = json.loads(run_command(command, self.scratch))
        self.assertTrue(all(item["status"] == "unchanged" for item in second["skills"]))
        self.assertEqual(sorted(p.name for p in destination.iterdir()), names)
        output = run_command([sys.executable, str(destination / "fenix-read/scripts/fetch_local.py"),
                              "--help"], self.scratch)
        self.assertIn("usage:", output)

    def test_install_preview_is_read_only_and_excludes_project_workflows(self):
        self.fixture()
        hidden = self.source / "skills/.local"
        hidden.mkdir()
        (hidden / "private.txt").write_text("not a skill")
        plan = install_local(self.source, self.destination)
        self.assertEqual([item["name"] for item in plan], ["fenix-alpha", "fenix-beta"])
        self.assertTrue(all(item["status"] == "create" for item in plan))
        self.assertFalse(self.destination.exists())

    def test_install_keeps_resources_and_is_idempotent(self):
        self.fixture()
        helper = self.source / "skills/fenix-alpha/scripts/probe.py"
        helper.parent.mkdir()
        helper.write_text("print('installed-resource-ok')\n")
        install_local(self.source, self.destination, apply=True)
        self.assertEqual((self.destination / "fenix-alpha/LICENSE").read_text(), "Fixture license\n")
        output = run_command([sys.executable, str(self.destination / "fenix-alpha/scripts/probe.py")], self.scratch)
        self.assertEqual(output.strip(), "installed-resource-ok")
        repeated = install_local(self.source, self.destination, apply=True)
        self.assertTrue(all(item["status"] == "unchanged" for item in repeated))
        self.assertEqual(len(list(self.destination.iterdir())), 2)
        self.assertFalse((self.destination / "fenix-private").exists())

    def test_conflicts_prevent_all_writes(self):
        self.fixture()
        for kind in ("directory", "broken-link", "other-source"):
            destination = self.scratch / kind
            destination.mkdir()
            target = destination / "fenix-beta"
            if kind == "directory":
                target.mkdir()
                (target / "keep").write_text("existing")
            else:
                target.symlink_to(self.scratch / ("missing" if kind == "broken-link" else "repo"))
            with self.subTest(kind=kind), self.assertRaisesRegex(HarnessError, "Existing installations"):
                install_local(self.source, destination, apply=True)
            self.assertFalse((destination / "fenix-alpha").exists())
            if kind == "directory":
                self.assertEqual((target / "keep").read_text(), "existing")
            else:
                self.assertTrue(target.is_symlink())

    def test_invalid_source_never_creates_destination(self):
        self.fixture()
        (self.source / "skills/fenix-beta/SKILL.md").write_text("# No metadata\n")
        with self.assertRaisesRegex(HarnessError, "Invalid source repository"):
            install_local(self.source, self.destination, apply=True)
        self.assertFalse(self.destination.exists())

    def test_partial_failure_or_interrupt_rolls_back_only_new_links(self):
        self.fixture()
        original = Path.symlink_to
        self.destination.mkdir()
        sentinel = self.destination / "keep.txt"
        sentinel.write_text("existing")
        for error in (OSError("synthetic failure"), KeyboardInterrupt()):
            def create(target, *args, **kwargs):
                if target.name == "fenix-beta":
                    raise error
                return original(target, *args, **kwargs)

            with self.subTest(error=type(error).__name__), patch.object(Path, "symlink_to", create):
                with self.assertRaises(type(error)):
                    install_local(self.source, self.destination, apply=True)
            self.assertEqual(list(self.destination.iterdir()), [sentinel])
            self.assertEqual(sentinel.read_text(), "existing")


if __name__ == "__main__":
    unittest.main()
