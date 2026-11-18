import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class IntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="integration test ")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / "pkg").mkdir()
        self.first = self.home / "first ' prefix"
        self.second = self.home / "second prefix"
        for prefix in (self.first, self.second, self.home):
            (prefix / "bin").mkdir(parents=True)
        (self.home / ".shell-common").symlink_to(ROOT / "shell-common")
        self.trace = self.home / "trace"

    def tool(self, prefix, name, body="exit 0\n"):
        file = prefix / "bin" / name
        file.write_text("#!/bin/sh\n" + body)
        file.chmod(0o755)
        return file

    def resource(self, prefix, relative, body):
        file = prefix / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(body)

    def run_shell(self, file, body, interactive=False, before="", shell="/bin/bash"):
        return subprocess.run(
            [shell, "--noprofile", "--norc", "-ic" if interactive else "-c",
             'hostname() { printf "%s\\n" "$TEST_HOST"; }; ssh-add() { return 0; }; '
             + (before or ":") + '; . "$1"; ' + body, "integration-test", str(ROOT / file)],
            env={**os.environ, "HOME": str(self.home), "TEST_HOST": "dotfiles-test",
                 "PATH": str(self.first / "bin") + ":" + str(self.second / "bin"),
                 "USER": "dotfiles-test", "SSH_AUTH_SOCK": "/tmp/ssh-agent-dotfiles-test-tmux",
                 "TMUX": "", "INTELLIJ_ENVIRONMENT_READER": "", "ENV": "", "BASH_ENV": "",
                 "HISTFILE": "/dev/null", "TRACE": str(self.trace)},
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15,
        )

    def test_profile_discovers_home_bin_tools_after_establishing_path(self):
        delta = self.tool(self.home, "delta")
        self.tool(self.home, "highlight")
        self.tool(self.home, "bat")
        result = self.run_shell("profile", 'printf "%s\\n" "$GIT_PAGER" "$LESSOPEN" "$MANPAGER"')
        self.assertEqual(result.returncode, 0, result.stderr)
        pager, lessopen, manpager = result.stdout.splitlines()
        self.assertEqual(shlex.split(pager), [str(delta)])
        self.assertEqual(shlex.split(lessopen)[1], str(self.home / "bin/highlight"))
        self.assertIn(str(self.home / "bin/bat"), shlex.split(manpager)[2])

    def test_nonlogin_rc_uses_selected_commands_and_discards_failed_hook_output(self):
        self.tool(self.first, "bat", "printf selected-bat\n")
        self.tool(self.second, "bat", "printf wrong-bat\n")
        self.tool(self.first, "direnv", "printf '%s\\n' 'export DIRENV_TEST=selected'\n")
        self.tool(self.first, "sheldon", "printf '%s\\n' 'export SHELDON_TEST=selected'\n")
        self.tool(self.first, "zoxide", "printf '%s\\n' 'export ZOXIDE_TEST=selected'\n")
        self.tool(self.first, "starship", "printf '%s\\n' 'export FAILED_HOOK_EXECUTED=yes'; exit 1\n")
        result = self.run_shell(
            "bashrc", 'eval "cat"; printf "|%s|%s|%s|%s\\n" "$DIRENV_TEST" '
            '"$SHELDON_TEST" "$ZOXIDE_TEST" "${FAILED_HOOK_EXECUTED-no}"; HISTFILE=/dev/null',
            interactive=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "selected-bat|selected|selected|selected|no\n")

    def test_hook_initialization_status_does_not_fail_rc(self):
        self.tool(self.first, "zoxide", "printf '%s\\n' false\n")
        result = self.run_shell("bashrc", 'printf "%s\\n" "$?"; HISTFILE=/dev/null', interactive=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "0\n")

    def test_support_files_use_selected_git_and_running_bash(self):
        running_bash = self.tool(self.first, "bash")
        self.tool(self.second, "bash")
        self.tool(self.second, "git")
        self.resource(self.second, "share/examples/git/git-prompt.sh",
                      "export PROMPT_TEST=selected\n__git_ps1() { :; }\n")
        self.resource(self.first, "share/bash-completion/bash_completion", "export COMPLETION_TEST=running\n")
        self.resource(self.second, "share/bash-completion/bash_completion", "export COMPLETION_TEST=wrong\n")
        result = self.run_shell(
            "bashrc", 'printf "%s|%s\\n" "$PROMPT_TEST" "$COMPLETION_TEST"; HISTFILE=/dev/null',
            interactive=True, before='BASH=' + shlex.quote(str(running_bash)),
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        # Old Bash intentionally skips optional completion, but still loads Git's prompt.
        version = subprocess.check_output(["/bin/bash", "-c", 'printf "%s.%s" "${BASH_VERSINFO[0]}" "${BASH_VERSINFO[1]}"'], text=True)
        major, minor = map(int, version.split('.'))
        expected = "running" if (major, minor) >= (4, 2) else ""
        self.assertEqual(result.stdout, "selected|" + expected + "\n")

    def test_missing_helper_preserves_basic_profile_and_rc(self):
        (self.home / ".shell-common").unlink()
        result = self.run_shell("profile", 'printf "%s|%s\\n" "$CVS_RSH" "$GIT_PAGER"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "ssh|less -x9,17,25\n")
        (self.home / ".xsh").write_text("printf customization\n")
        result = self.run_shell("bashrc", 'printf continued; HISTFILE=/dev/null', interactive=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "customizationcontinued")
        self.assertNotIn("command not found", result.stderr)

    def test_directory_in_place_of_helper_is_ignored(self):
        (self.home / ".shell-common").unlink()
        (self.home / ".shell-common").mkdir()
        result = self.run_shell("profile", 'printf continued')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "continued")
        self.assertEqual(result.stderr, "")
        result = self.run_shell("bashrc", 'printf continued; HISTFILE=/dev/null', interactive=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "continued")
        self.assertNotIn(".shell-common", result.stderr)

    def run_iterm2_rc(self, terminal, installed=True):
        if installed:
            (self.home / ".iterm2_shell_integration.bash").write_text('printf "iterm2-loaded\\n"\n')
        return self.run_shell(
            "bashrc", 'printf continued; HISTFILE=/dev/null', interactive=True,
            before="unset LC_TERMINAL TERM_PROGRAM; " + terminal)

    def test_iterm2_integration_is_skipped_outside_iterm2(self):
        for installed in (True, False):
            result = self.run_iterm2_rc("export TERM_PROGRAM=WezTerm", installed)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, "continued")
            self.assertNotIn("iTerm2", result.stderr)

    def test_iterm2_integration_loads_in_local_iterm2(self):
        result = self.run_iterm2_rc("export TERM_PROGRAM=iTerm.app")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "iterm2-loaded\ncontinued")

    def test_iterm2_integration_loads_over_ssh_from_iterm2(self):
        result = self.run_iterm2_rc("export LC_TERMINAL=iTerm2")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "iterm2-loaded\ncontinued")

    def test_missing_iterm2_integration_is_reported_in_iterm2(self):
        result = self.run_iterm2_rc("export TERM_PROGRAM=iTerm.app", installed=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "continued")
        self.assertIn("Install Shell Integration", result.stderr)

    def test_iterm2_installer_finds_existing_hook_in_rc_files(self):
        # iTerm2's installer appends to an rc file unless it already mentions this name.
        for name in ("bashrc", "profile"):
            self.assertIn("iterm2_shell_integration", (ROOT / name).read_text(), name)

    def test_existing_host_rule_can_start_native_tmux(self):
        self.tool(self.home, "tmux", 'printf "%s\\n" "$*" >> "$TRACE"; exit 0\n')
        result = self.run_shell("profile", "printf should-not-reach", interactive=True,
                                before="TEST_HOST=pet-power-plant")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.trace.exists(), result.stdout + result.stderr)
        self.assertEqual(self.trace.read_text(), "attach\n")
        self.assertNotIn("should-not-reach", result.stdout)
