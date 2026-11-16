import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class DiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="discovery test ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.first = self.root / "first prefix"
        self.second = self.root / "second prefix"
        for prefix in (self.first, self.second):
            (prefix / "bin").mkdir(parents=True)
        self.path = str(self.first / "bin") + ":" + str(self.second / "bin")
        self.shells = ["/bin/sh", "/bin/bash", "/bin/ksh", "/bin/zsh",
                       "/opt/pkg/bin/bash", "/opt/pkg/bin/zsh"]
        self.shells = [shell for shell in self.shells if os.access(shell, os.X_OK)]

    def executable(self, prefix, name):
        path = prefix / "bin" / name
        path.write_text("#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
        return path

    def resource(self, prefix, relative):
        path = prefix / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("resource\n")
        return path

    def run_code(self, shell, code, path=None, cwd=None):
        workdir = self.root if cwd is None else cwd
        return subprocess.run(
            [shell, "-c", '. "$1"; PATH=$2; export PATH; ' + code,
             "discovery-test", str(ROOT / "shell-common"), self.path if path is None else path],
            cwd=workdir, env={**os.environ, "PATH": self.path if path is None else path,
                              "PWD": str(workdir.resolve()), "ENV": "", "BASH_ENV": ""},
            capture_output=True, text=True, timeout=10,
        )

    def assert_lookup(self, code, expected, path=None, cwd=None):
        for shell in self.shells:
            with self.subTest(shell=shell, path=path):
                result = self.run_code(shell, code, path, cwd)
                self.assertEqual(result.returncode, 0, result.stderr)
                if isinstance(expected, Path):
                    self.assertEqual(Path(result.stdout.strip()).resolve(), expected.resolve())
                else:
                    self.assertEqual(result.stdout.strip(), expected)
                self.assertEqual(result.stderr, "")

    def test_command_uses_path_order_and_ignores_aliases_and_functions(self):
        first = self.executable(self.first, "tool")
        self.executable(self.second, "tool")
        self.assert_lookup("alias tool='false'; tool() { false; }; _dotfiles_command tool", first)
        self.assert_lookup("_dotfiles_command tool", self.second / "bin/tool",
                           str(self.second / "bin") + ":" + str(self.first / "bin"))

    def test_command_skips_nonexecutables_and_directories(self):
        (self.first / "bin/tool").mkdir()
        second = self.executable(self.second, "tool")
        self.assert_lookup("_dotfiles_command tool", second)
        (self.first / "bin/tool").rmdir()
        (self.first / "bin/tool").write_text("not executable")
        self.assert_lookup("_dotfiles_command tool", second)

    def test_relative_and_empty_path_entries(self):
        local = self.root / "tool"
        local.write_text("#!/bin/sh\nexit 0\n")
        local.chmod(0o755)
        self.assert_lookup("_dotfiles_command tool", local, ":" + self.path)
        self.assert_lookup("_dotfiles_command tool", local, "")
        self.executable(self.first, "tool")
        self.assert_lookup("_dotfiles_command tool", self.first / "bin/tool", "first prefix/bin")

    def test_missing_command_is_quiet(self):
        for shell in self.shells:
            with self.subTest(shell=shell):
                result = self.run_code(shell, "_dotfiles_command absent")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout + result.stderr, "")

    def test_selected_installation_resource_precedes_other_path_prefixes(self):
        self.executable(self.first, "tool")
        self.executable(self.second, "tool")
        self.resource(self.first, "share/example/resource")
        chosen = self.resource(self.second, "share/example/resource")
        self.assert_lookup(
            '_dotfiles_support_file "' + str(self.second / "bin/tool") + '" share/example/resource',
            chosen,
        )

    def test_resource_falls_back_in_path_order_and_checks_candidate_layouts(self):
        self.executable(self.first, "tool")
        chosen = self.resource(self.second, "share/other/resource")
        self.assert_lookup(
            "_dotfiles_support_file tool share/example/resource share/other/resource", chosen,
        )

    def test_resources_with_empty_or_dot_path_entries(self):
        self.executable(self.first, "tool")
        resource = self.resource(self.first, "share/resource")
        for path in ("", ".", "../bin", "../bin/."):
            self.assert_lookup('_dotfiles_support_file tool share/resource',
                               resource, path, self.first / "bin")

    def test_missing_resource_and_directory_are_quiet(self):
        self.executable(self.first, "tool")
        (self.first / "share/resource").mkdir(parents=True)
        for shell in self.shells:
            with self.subTest(shell=shell):
                result = self.run_code(shell, "_dotfiles_support_file tool share/resource")
                self.assertNotEqual(result.returncode, 0)
                self.assertEqual(result.stdout + result.stderr, "")

    def test_lookup_preserves_caller_state(self):
        self.executable(self.first, "tool")
        self.resource(self.first, "share/resource")
        code = '''
            before_path=$PATH; before_ifs=$IFS; before_flags=$-; before_cwd=$PWD
            _dotfiles_command tool >/dev/null
            _dotfiles_support_file tool share/resource >/dev/null
            [ "$PATH" = "$before_path" ] && [ "$IFS" = "$before_ifs" ] &&
            [ "$-" = "$before_flags" ] && [ "$PWD" = "$before_cwd" ] && printf preserved
        '''
        self.assert_lookup(code, "preserved")
