"""Fenix checkout inventory, scoped verification and local skill installation."""

import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
if __package__ in (None, ""):
    sys.path.insert(0, str(ROOT))

from scripts.verify_repo import verify


class HarnessError(RuntimeError):
    pass


def run_command(args, cwd, timeout=120, output_limit=1024 * 1024):
    """Bound execution and combined output; clean up children on interruption."""
    with tempfile.TemporaryFile() as output:
        process = subprocess.Popen(args, cwd=cwd, stdout=output, stderr=output,
                                   start_new_session=os.name == "posix")

        def stop():
            try:
                if os.name == "posix":
                    os.killpg(process.pid, signal.SIGKILL)
                elif process.poll() is None:
                    process.kill()
            except ProcessLookupError:
                pass
            process.wait()

        reason = None
        deadline = time.monotonic() + timeout
        try:
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    reason = "timeout after {}s".format(timeout)
                    break
                if os.fstat(output.fileno()).st_size > output_limit:
                    reason = "output limit exceeded ({} bytes)".format(output_limit)
                    break
                time.sleep(0.02)
        finally:
            stop()
        if os.fstat(output.fileno()).st_size > output_limit:
            reason = reason or "output limit exceeded ({} bytes)".format(output_limit)
        output.seek(0)
        text = output.read(output_limit).decode("utf-8", errors="replace")
        if reason or process.returncode:
            raise HarnessError("{}: {}\n{}".format(
                args[0], reason or "exit {}".format(process.returncode), text))
        return text


def checkout_scope(root=ROOT):
    def git(*args):
        return run_command(["git", *args], root, timeout=15)

    head = git("rev-parse", "HEAD").strip()
    branch = git("branch", "--show-current").strip()
    upstream = git("for-each-ref", "--format=%(upstream:short)",
                   "refs/heads/" + branch).strip() if branch else ""
    records = iter(git("status", "--porcelain=v1", "-z", "--untracked-files=all").split("\0"))
    changes = []
    for record in records:
        if not record:
            continue
        change = {"status": record[:2], "path": record[3:]}
        if "R" in record[:2] or "C" in record[:2]:
            change["previous_path"] = next(records)
        changes.append(change)
    result = {"root": str(root), "head": head, "branch": branch or None,
              "upstream": upstream or None, "changes": changes,
              "recent": git("log", "-5", "--format=%h %s").splitlines()}
    if git("rev-parse", "HEAD").strip() != head:
        raise HarnessError("HEAD changed during inventory; run scope again")
    return result


def verification_plan(scope, python=sys.executable):
    if scope not in ("repository", "full"):
        raise HarnessError("Expected scope: repository or full")
    targets = ["verify-docs", "verify-scripts"]
    if scope == "full":
        targets.append("verify-unit")
    return [["make", target, "PYTHON=" + python] for target in targets]


def verify_scope(scope, root=ROOT, runner=run_command):
    plan = verification_plan(scope)
    completed = []
    for command in plan:
        stage = command[1]
        print("Checking: " + stage, flush=True)
        try:
            output = runner(command, root)
        except (OSError, HarnessError) as exc:
            raise HarnessError("Stopped at {}; completed: {}\n{}".format(
                stage, ", ".join(completed) or "none", exc)) from exc
        if output:
            print(output, end="" if output.endswith("\n") else "\n", flush=True)
        completed.append(stage)
    print("Verification passed: " + ", ".join(completed), flush=True)
    return completed


def install_plan(root, destination):
    errors, count = verify(root)
    if errors:
        raise HarnessError("Invalid source repository:\n" + "\n".join(errors))
    if not count:
        raise HarnessError("No public skills to install")
    if destination.exists() and not destination.is_dir():
        raise HarnessError("Install destination is not a directory: " + str(destination))
    result = []
    for source in sorted((root / "skills").iterdir()):
        if not source.is_dir() or source.name.startswith("."):
            continue
        target = destination / source.name
        status = "create"
        if target.exists() or target.is_symlink():
            status = "unchanged" if target.is_symlink() and target.resolve() == source.resolve() else "conflict"
        result.append({"name": source.name, "source": str(source.resolve()),
                       "target": str(target), "status": status})
    return result


def install_local(root, destination, apply=False):
    plan = install_plan(root, destination)
    conflicts = [item["target"] for item in plan if item["status"] == "conflict"]
    if conflicts:
        raise HarnessError("Existing installations were not changed:\n" + "\n".join(conflicts))
    if not apply:
        return plan
    destination.mkdir(parents=True, exist_ok=True)
    created = []
    try:
        for item in plan:
            if item["status"] != "create":
                continue
            target = Path(item["target"])
            target.symlink_to(item["source"], target_is_directory=True)
            created.append(item)
    except (OSError, KeyboardInterrupt):
        for item in reversed(created):
            target = Path(item["target"])
            if target.is_symlink() and os.readlink(target) == item["source"]:
                target.unlink()
        raise
    return plan


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("scope", help="Read-only Git checkout inventory")
    check = commands.add_parser("verify", help="Run checks and stop on first failure")
    check.add_argument("--scope", choices=["repository", "full"], required=True)
    install = commands.add_parser("install", help="Preview local links; --apply installs")
    default_home = Path(os.environ.get("CODEX_HOME") or str(Path.home() / ".codex"))
    install.add_argument("--dest", type=Path, default=default_home / "skills")
    install.add_argument("--apply", action="store_true")
    args = parser.parse_args(argv)
    try:
        if args.command == "scope":
            result = checkout_scope()
        elif args.command == "verify":
            verify_scope(args.scope)
            return 0
        else:
            result = {"applied": args.apply, "skills": install_local(
                ROOT, args.dest.expanduser().absolute(), apply=args.apply)}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, HarnessError) as exc:
        print("ERROR: " + str(exc), file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    sys.exit(main())
