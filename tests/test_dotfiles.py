import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
MAKE = os.environ.get("TEST_MAKE", "make")


class DotfilesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="dotfiles test ")
        self.addCleanup(self.tmp.cleanup)
        workspace = Path(self.tmp.name).resolve()
        self.home = workspace / "home"
        self.home.mkdir()
        self.checkout = workspace / "arbitrary parent" / "dotfiles"
        shutil.copytree(
            ROOT, self.checkout, symlinks=True,
            ignore=shutil.ignore_patterns(".git", "__pycache__", ".superpowers"),
        )

    def link(self, source, destination, *options, env=None):
        return subprocess.run(
            ["sh", str(self.checkout / "scripts/link-dotfile"),
             *options, str(source), str(destination)],
            capture_output=True, text=True, env=env,
        )

    def as_other_user(self):
        # Files owned by someone else (e.g. an NFS checkout with mismatched UIDs) need root to create.
        fake = self.home / "fake bin"
        fake.mkdir(exist_ok=True)
        (fake / "id").write_text('#!/bin/sh\n[ "$1" = -u ] && echo 999999 && exit 0\nexec /usr/bin/id "$@"\n')
        (fake / "id").chmod(0o755)
        return {**os.environ, "PATH": str(fake) + ":" + os.environ["PATH"]}

    def private_source(self, text="source"):
        source = self.home / "source with spaces"
        source.write_text(text)
        return source, self.home / "private destination"

    def test_private_links_source_owned_by_user(self):
        source, destination = self.private_source()
        result = self.link(source, destination, "--private")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(destination.resolve(), source)

    def test_private_copies_and_refreshes_source_owned_by_other_user(self):
        source, destination = self.private_source()
        destination.symlink_to(source)
        for text in ("source", "source", "updated"):
            source.write_text(text)
            result = self.link(source, destination, "--private", env=self.as_other_user())
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(destination.is_symlink())
            self.assertEqual(destination.read_text(), text)
            self.assertEqual(destination.stat().st_mode & 0o777, 0o600)

    def test_private_preserves_edited_copy(self):
        source, destination = self.private_source()
        self.assertEqual(self.link(source, destination, "--private", env=self.as_other_user()).returncode, 0)
        destination.write_text("edited")
        source.write_text("updated")
        result = self.link(source, destination, "--private", env=self.as_other_user())
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to replace", result.stderr)
        self.assertEqual(destination.read_text(), "edited")

    def test_private_preserves_unrelated_local_file(self):
        source, destination = self.private_source()
        destination.write_text("local")
        result = self.link(source, destination, "--private", env=self.as_other_user())
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_text(), "local")

    def test_private_copy_becomes_link_once_source_is_owned(self):
        source, destination = self.private_source()
        self.assertEqual(self.link(source, destination, "--private", env=self.as_other_user()).returncode, 0)
        source.write_text("updated")
        result = self.link(source, destination, "--private")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(destination.resolve(), source)
        self.assertEqual(sorted(p.name for p in self.home.iterdir() if "destination" in p.name),
                         ["private destination"])

    def test_create_repeat_and_repair_broken_link(self):
        source = self.home / "source with spaces"
        source.write_text("source")
        destination = self.home / "destination"
        destination.symlink_to(self.home / "missing")
        for _ in range(2):
            self.assertEqual(self.link(source, destination).returncode, 0)
            self.assertEqual(destination.resolve(), source)

    def test_replaces_symlink_to_directory_not_contents(self):
        source = self.home / "source"
        source.mkdir()
        old = self.home / "old"
        old.mkdir()
        destination = self.home / "destination"
        destination.symlink_to(old)
        self.assertEqual(self.link(source, destination).returncode, 0)
        self.assertEqual(destination.resolve(), source)
        self.assertEqual(list(old.iterdir()), [])

    def test_preserves_local_files_and_directories(self):
        source = self.home / "source"
        source.write_text("source")
        destination = self.home / "local file"
        destination.write_text("local")
        self.assertNotEqual(self.link(source, destination).returncode, 0)
        self.assertEqual(destination.read_text(), "local")
        directory = self.home / "local directory"
        directory.mkdir()
        self.assertNotEqual(self.link(source, directory).returncode, 0)
        self.assertEqual(list(directory.iterdir()), [])

    def test_missing_source_preserves_existing_link(self):
        destination = self.home / "destination"
        destination.symlink_to("old")
        self.assertNotEqual(self.link(self.home / "missing", destination).returncode, 0)
        self.assertEqual(os.readlink(destination), "old")

    def test_allow_missing_creates_and_repeats_dangling_link(self):
        source = self.home / "not downloaded yet" / "skill"
        destination = self.home / "destination"
        for _ in range(2):
            result = self.link(source, destination, "--allow-missing")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(destination.is_symlink())
            self.assertEqual(os.readlink(destination), str(source))
        source.mkdir(parents=True)
        self.assertTrue(destination.is_dir())

    def test_allow_missing_still_preserves_local_file(self):
        destination = self.home / "destination"
        destination.write_text("local")
        result = self.link(self.home / "missing", destination, "--allow-missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(destination.read_text(), "local")

    def make(self, *targets):
        return subprocess.run(
            [MAKE, *targets], cwd=self.checkout,
            env={**os.environ, "HOME": str(self.home)},
            capture_output=True, text=True,
        )

    def test_default_install_without_external_checkouts_and_repeat(self):
        for _ in range(2):
            result = self.make("-j4", "dotfiles")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        expected = {
            ".shell-common": "shell-common",
            ".claude/settings.json": "agents/claude/settings.json",
            ".codex/config.toml": "agents/codex/config.toml",
            ".codex/AGENTS.md": "agents/codex/AGENTS.md",
            ".pi/agent/settings.json": "agents/pi/settings.json",
            ".pi/agent/i-have-adhd.json": "agents/pi/i-have-adhd.json",
            ".ssh/config": "ssh-config",
            ".profile": "profile",
        }
        for destination, source in expected.items():
            self.assertEqual((self.home / destination).resolve(), self.checkout / source)
        for name in ("doubt-driven-development", "mavergreen-conventions"):
            link = self.home / ".agents/skills" / name
            self.assertTrue(link.is_symlink())
            self.assertFalse(link.exists())

    def test_skill_links_resolve_when_external_checkouts_arrive(self):
        result = self.make("dotfiles-agents")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        doubt = self.home / ".pi/agent/git/github.com/addyosmani/agent-skills/skills/doubt-driven-development"
        mavergreen = self.checkout.parent / "mavergreen-shipyard/claude-plugins/mavergreen/skills/mavergreen-conventions"
        for source in (doubt, mavergreen):
            source.mkdir(parents=True)
            (source / "SKILL.md").write_text("downloaded skill")
        for name, source in (("doubt-driven-development", doubt), ("mavergreen-conventions", mavergreen)):
            link = self.home / ".agents/skills" / name
            self.assertEqual(link.resolve(strict=True), source)
            self.assertEqual((link / "SKILL.md").read_text(), "downloaded skill")
        self.assertFalse((self.home / "trees").exists())

    def test_make_reports_conflict(self):
        (self.home / ".ackrc").write_text("local")
        result = self.make("dotfiles-typical")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing to replace", result.stderr)
        self.assertEqual((self.home / ".ackrc").read_text(), "local")

    def test_missing_repository_source_still_fails(self):
        (self.checkout / "agents/pi/settings.json").unlink()
        result = self.make("dotfiles-agents-pi")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Missing dotfile source:", result.stderr)
        self.assertFalse((self.home / ".pi/agent/settings.json").is_symlink())

    def test_helper_conflict_prevents_shell_link_installation(self):
        (self.home / ".shell-common").write_text("local")
        result = self.make("-j4", "dotfiles-typical")
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual((self.home / ".shell-common").read_text(), "local")
        self.assertFalse((self.home / ".bashrc").exists())

    @unittest.skipUnless(shutil.which("ssh"), "needs ssh")
    def test_ssh_config_forwards_agent_only_on_request(self):
        resolved = subprocess.run(
            ["ssh", "-G", "-F", str(self.checkout / "ssh-config"), "any-host.example"],
            capture_output=True, text=True,
        )
        self.assertEqual(resolved.returncode, 0, resolved.stderr)
        self.assertIn("forwardagent no", resolved.stdout.splitlines())

    def test_agent_json_is_valid(self):
        for path in (self.checkout / "agents").rglob("*.json"):
            json.loads(path.read_text())
