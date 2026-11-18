import os
from pathlib import Path
import shlex
import socket
import subprocess
import tempfile
import unittest

from shells import available_shells, without_startup_files


ROOT = Path(__file__).resolve().parents[1]
PRINT_SOCK = 'printf "%s\\n" "${SSH_AUTH_SOCK-unset}"'
SYSTEM_SOCK = "/tmp/ssh-agent-dotfiles-test-tmux"
# A function named ssh-add is a syntax error in ksh and dash, so profile finds this in ~/bin.
FAKE_SSH_ADD = """printf '%s\\n' "$*" >> "$HOME/ssh-add.log"
[ "$1" = -l ] && exit "${SSH_ADD_LIST_STATUS-0}"
exit 0
"""


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
        self.tool(self.home, "ssh-add", FAKE_SSH_ADD)
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

    def run_shell(self, file, body, interactive=False, before="", shell="/bin/bash", home=None):
        return subprocess.run(
            [shell, *without_startup_files(shell), "-ic" if interactive else "-c",
             'hostname() { printf "%s\\n" "$TEST_HOST"; }; '
             + (before or ":") + '; . "$1"; ' + body, "integration-test", str(ROOT / file)],
            env={**os.environ, "HOME": str(home or self.home), "TEST_HOST": "dotfiles-test",
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

    def quoted_home(self):
        home = self.home / "o'q\"h"
        (home / "bin").mkdir(parents=True)
        (home / ".shell-common").symlink_to(ROOT / "shell-common")
        self.tool(home, "ssh-add", FAKE_SSH_ADD)
        return home

    def agent_socket(self, home=None):
        directory = (home or self.home) / ".1password"
        directory.mkdir()
        server = socket.socket(socket.AF_UNIX)
        self.addCleanup(server.close)
        cwd = os.getcwd()
        os.chdir(directory)  # sun_path is short; bind relative to stay under it
        try:
            server.bind("agent.sock")
        finally:
            os.chdir(cwd)
        return directory / "agent.sock"

    def check_profile_everywhere(self, home, before, check):
        for shell in available_shells():
            with self.subTest(shell=shell):
                (home / "ssh-add.log").unlink(missing_ok=True)
                result = self.run_shell("profile", PRINT_SOCK, before=before, shell=shell, home=home)
                self.assertEqual(result.returncode, 0, result.stderr)
                check(result)

    def assert_profile_sock(self, home, expected, before="unset SSH_CONNECTION"):
        self.check_profile_everywhere(home, before, lambda result:
            self.assertEqual(result.stdout, str(expected) + "\n"))

    def ssh_add_calls(self, home):
        log = home / "ssh-add.log"
        return log.read_text().splitlines() if log.exists() else []

    def test_profile_selects_1password_agent_socket(self):
        home = self.quoted_home()
        self.assert_profile_sock(home, self.agent_socket(home))

    def test_profile_keeps_system_agent_without_1password_socket(self):
        self.assert_profile_sock(self.quoted_home(), SYSTEM_SOCK)

    def test_profile_ignores_non_socket_at_1password_path(self):
        home = self.quoted_home()
        (home / ".1password").mkdir()
        (home / ".1password/agent.sock").write_text("")
        self.assert_profile_sock(home, SYSTEM_SOCK)

    def test_profile_keeps_forwarded_agent(self):
        home = self.quoted_home()
        self.agent_socket(home)
        self.assert_profile_sock(home, "/tmp/forwarded", before=
            'export SSH_CONNECTION="10.0.0.1 1 10.0.0.2 22" SSH_AUTH_SOCK=/tmp/forwarded')

    def test_profile_selects_1password_in_ssh_session_without_forwarding(self):
        home = self.quoted_home()
        sock = self.agent_socket(home)
        self.assert_profile_sock(home, sock, before=
            'export SSH_CONNECTION="10.0.0.1 1 10.0.0.2 22"; unset SSH_AUTH_SOCK')

    def test_profile_loads_keychain_into_empty_system_agent(self):
        home = self.quoted_home()
        self.check_profile_everywhere(home, "unset SSH_CONNECTION; export SSH_ADD_LIST_STATUS=1",
            lambda _: self.assertEqual(self.ssh_add_calls(home), ["-l", "--apple-load-keychain"]))

    def test_profile_does_not_load_keychain_into_1password_agent(self):
        # 1Password's agent refuses added keys; asking is a wasted call at every login.
        home = self.quoted_home()
        self.agent_socket(home)
        self.check_profile_everywhere(home, "unset SSH_CONNECTION; export SSH_ADD_LIST_STATUS=1",
            lambda _: self.assertNotIn("--apple-load-keychain", self.ssh_add_calls(home)))

    def test_profile_starts_agent_with_keychain_without_naming_a_key(self):
        # AddKeysToAgent loads whichever key ssh uses; naming one here would miss the rest.
        home = self.quoted_home()
        self.tool(home, "keychain", 'printf "%s\\n" "$*" >> "$HOME/keychain.log"\n')
        log = home / "keychain.log"
        def check(_):
            self.assertEqual(log.read_text(), "--quiet --eval --agents ssh --inherit any\n")
            log.unlink()
        self.check_profile_everywhere(home, "unset SSH_CONNECTION SSH_AUTH_SOCK", check)

    def test_tmux_host_links_predictable_socket_to_1password(self):
        sock = self.agent_socket()
        # A per-run name, so another user's or another run's link can't collide in /tmp.
        user = "dotfiles-test-" + self.home.name.rsplit(" ", 1)[-1]
        link = Path("/tmp/ssh-agent-" + user + "-tmux")
        self.addCleanup(lambda: link.unlink() if link.is_symlink() else None)
        self.tool(self.home, "tmux", "exit 0\n")
        result = self.run_shell("profile", "printf should-not-reach", interactive=True,
                                before="unset SSH_CONNECTION; TEST_HOST=pet-power-plant; USER=" + user)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(link.is_symlink(), result.stderr)
        self.assertEqual(os.readlink(link), str(sock))
        self.assertFalse(Path(SYSTEM_SOCK).is_symlink())

    def test_existing_host_rule_can_start_native_tmux(self):
        self.tool(self.home, "tmux", 'printf "%s\\n" "$*" >> "$TRACE"; exit 0\n')
        result = self.run_shell("profile", "printf should-not-reach", interactive=True,
                                before="TEST_HOST=pet-power-plant")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(self.trace.exists(), result.stdout + result.stderr)
        self.assertEqual(self.trace.read_text(), "attach\n")
        self.assertNotIn("should-not-reach", result.stdout)
