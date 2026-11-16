import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ShellStartupTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="shell startup test ")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / ".shell-common").symlink_to(ROOT / "shell-common")
        # Keep optional pkgsrc tools out of this startup test.
        (self.home / "pkg").mkdir()
        (self.home / ".xsh").write_text("printf '%s\\n' 'interactive setup reached'\n")

    def run_shell(self, shell, interactive):
        options = []
        name = Path(shell).name
        if name == "bash":
            options = ["--noprofile", "--norc"]
        elif name == "zsh":
            options = ["-f"]
        return subprocess.run(
            [shell, *options, "-ic" if interactive else "-c",
             '. "$1"; startup_status=$?; HISTFILE=/dev/null; '
             'printf "startup status=%s\\n" "$startup_status"; '
             'printf "%s\\n" "body executed"',
             "startup-test", str(ROOT / "bashrc")],
            env={**os.environ, "HOME": str(self.home),
                 "ZDOTDIR": str(self.home), "ENV": "", "BASH_ENV": "",
                 "HISTFILE": "/dev/null"},
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15,
        )

    def available_shells(self):
        # Exercise native shells plus pkgsrc variants when installed.
        candidates = ["/bin/sh", "/bin/bash", "/bin/ksh", "/bin/zsh",
                      "/opt/pkg/bin/bash", "/opt/pkg/bin/zsh",
                      "/usr/pkg/bin/bash", "/usr/pkg/bin/ksh", "/usr/pkg/bin/zsh"]
        for name in ("bash", "ksh", "zsh"):
            path = shutil.which(name)
            if path:
                candidates.append(path)
        return sorted({path for path in candidates if os.access(path, os.X_OK)})

    def test_noninteractive_sourcing_skips_interactive_setup(self):
        for shell in self.available_shells():
            with self.subTest(shell=shell):
                result = self.run_shell(shell, interactive=False)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "startup status=0\nbody executed\n")
                self.assertEqual(result.stderr, "")

    def test_interactive_sourcing_keeps_interactive_setup(self):
        for shell in self.available_shells():
            with self.subTest(shell=shell):
                result = self.run_shell(shell, interactive=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    result.stdout,
                    "interactive setup reached\nstartup status=0\nbody executed\n",
                )


class ZshStartupOrderTests(unittest.TestCase):
    def setUp(self):
        candidates = ["/bin/zsh", "/opt/pkg/bin/zsh", "/usr/pkg/bin/zsh"]
        path = shutil.which("zsh")
        if path:
            candidates.append(path)
        self.shells = sorted({path for path in candidates if os.access(path, os.X_OK)})
        if not self.shells:
            self.skipTest("Zsh is not installed")
        self.tmp = tempfile.TemporaryDirectory(prefix="zsh startup test ")
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        (self.home / "pkg").mkdir()
        (self.home / ".shell-common").symlink_to(ROOT / "shell-common")
        (self.home / ".zprofile").write_text(
            # Source the real profile without SSH/keychain or tmux side effects.
            "hostname() { printf '%s\\n' 'dotfiles-startup-test'; }\n"
            "ssh-add() { return 0; }\n"
            '. "$DOTFILES_TEST_PROFILE"\n'
        )
        (self.home / ".zshrc").write_text(
            'printf "zshrc environment=%s\\n" "${CVS_RSH-unset}"\n'
        )

    def run_zsh(self, shell, mode):
        return subprocess.run(
            [shell, "-d", mode,
             'printf "profile environment=%s\\n" "${CVS_RSH-unset}"; '
             'printf "%s\\n" "body executed"'],
            env={**os.environ, "HOME": str(self.home),
                 "ZDOTDIR": str(self.home), "DOTFILES_TEST_PROFILE": str(ROOT / "profile"),
                 "SSH_AUTH_SOCK": "/tmp/dotfiles-startup-test-unused-socket",
                 "HISTFILE": "/dev/null", "CVS_RSH": "not initialized"},
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=15,
        )

    def test_interactive_login_sources_zshrc_once_after_profile(self):
        for shell in self.shells:
            with self.subTest(shell=shell):
                result = self.run_zsh(shell, "-lic")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    result.stdout,
                    "zshrc environment=ssh\nprofile environment=ssh\nbody executed\n",
                )

    def test_interactive_nonlogin_still_sources_zshrc_once(self):
        for shell in self.shells:
            with self.subTest(shell=shell):
                result = self.run_zsh(shell, "-ic")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(
                    result.stdout,
                    "zshrc environment=not initialized\n"
                    "profile environment=not initialized\nbody executed\n",
                )

    def test_noninteractive_login_initializes_environment_without_zshrc(self):
        for shell in self.shells:
            with self.subTest(shell=shell):
                result = self.run_zsh(shell, "-lc")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stdout, "profile environment=ssh\nbody executed\n")
