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
