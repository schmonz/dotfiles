# Optional shell tools

`profile` and `bashrc` share the POSIX-shell functions in `shell-common`, installed
as `~/.shell-common`. `make dotfiles` installs that helper before linking
`profile` and `bashrc`; an existing installation can add just the helper with:

```sh
cd /path/to/dotfiles
make dotfiles-shell-common
```

No dependencies are downloaded. Before the helper is installed, optional
integrations are skipped and basic shell setup remains usable.

## Lookup policy

- Select external executables in effective `PATH` order. Shell aliases and
  functions are not executable installations and do not override this lookup.
- Establish the profile's configured `PATH` before looking for optional tools.
  Non-login interactive shells use their inherited `PATH`.
- Look for support files under the selected installation prefix first. When
  identifiable, a prefix is the parent of a `bin` or `sbin` directory; resolve
  directory symlinks with the shell's physical `cd`, not GNU `readlink -f`.
- Try remaining prefixes in `PATH` order when the selected prefix lacks a
  resource. Candidate relative layouts are explicit, generic file paths—not
  hostname or OS branches. A resource must be a readable regular file.
- For Bash completion, use the running shell's `$BASH`, not a different Bash
  executable on `PATH`. Skip optional Bash completion below Bash 4.2; basic
  shell completion is unaffected.

The existing aliases, pager settings, prompt integration and host-specific tmux
activation remain the consumers of these lookups. In particular, the existing
`pet-power-plant` auto-attach preference can now use native tmux.

Hook generators are invoked using their selected executable path. Their output
is evaluated only when generation succeeds; partial output from a failed
generator is discarded. Request hooks for the actual shell rather than feeding
Bash code to another shell. The existing zoxide POSIX fallback and sheldon
Bash/Zsh profile selection remain in place. `.xsh` remains the customization
point in its existing startup position.

There are no persistent discovery caches and no new machine-specific detection
exceptions. Revisit the design rather than adding one if a new layout cannot be
handled by the general prefix/resource rules.

## Tests

`make test` uses isolated command/resource layouts and available native/pkgsrc
shells. Cross-machine validation uses temporary copies of the startup files and
helper; it does not install them into the tested machines' home directories.
