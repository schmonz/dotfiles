# Agent dotfiles

Run make from inside this checkout. `make dotfiles` includes the Claude, Codex,
and Pi configuration by default; `make dotfiles-agents` installs just the agent
links. Individual targets are available as `dotfiles-agents-claude`,
`dotfiles-agents-codex`, and `dotfiles-agents-pi`. GNU make is not required.

Links are refreshed after a move and repeated runs are safe. Local files and
directories are **not overwritten**: back them up outside the destination before
running make. Failures are reported instead of hidden. The same linking rules
apply to the other dotfile targets. Repository-owned sources must exist; only
the two external shared skill links may initially dangle. Run `make test` for
installer tests (Python 3.7+ required). To test another make implementation, run
its test target, for example `bmake test`; the tests use that same make.

## External skills

The shared skills are links to external checkouts, not vendored copies. They do
not need to be downloaded before `make dotfiles` or any agent target:

1. `~/.agents/skills/doubt-driven-development` points into Pi's managed checkout
   at `~/.pi/agent/git/github.com/addyosmani/agent-skills/skills/doubt-driven-development`.
   Pi's settings declare that package, so Pi attempts to download it on startup.
   Offline mode or a failed download can leave the link dangling until a later
   successful installation.
2. `~/.agents/skills/mavergreen-conventions` points into the sibling checkout
   `../mavergreen-shipyard/claude-plugins/mavergreen/skills/mavergreen-conventions`,
   relative to this dotfiles checkout. The parent directory need not be `~/trees`.
   If needed, check out shipyard from inside this checkout:
   ```sh
   git clone https://github.com/Mavergreen/shipyard.git ../mavergreen-shipyard
   ```

Both links start working when their targets arrive; rerunning make is not needed.
Rerun make after moving the checkouts to refresh absolute links. Package versions
are unpinned and installation executes third-party code; review sources before
installing.

`~/.agents/skills` is the shared discovery location for Codex and Pi. Claude has
its own skill/plugin setup; the Mavergreen skill is supplied by its enabled
Mavergreen plugin. These symlinks do not install Claude or Codex plugins, nor do
they supply authentication. Check each client's plugin status after bootstrap.

## Local state

The settings files are live symlink targets. Clients can write runtime state
(such as Pi's device ID/changelog version and Codex's onboarding/trust entries)
back into this checkout. Review that churn before committing. Keep credentials,
auth files, histories, and sessions outside this repository.

Claude's optional review hooks run `~/.local/bin/gatherd-doubt-commit-hook` and
`~/.local/bin/gatherd-doubt-doc-hook` when those executables are installed. These
scripts are machine-local and are not installed by this repository.

Claude auto-mode environment/trust assumptions belong to the relevant project,
not the global settings. Machine-local hooks and settings must be reconciled
before replacing an existing regular settings file; the installer refuses to
silently discard them. Machine-local shell and SSH wrappers can likewise source
or include this checkout without being replaced by the installer.
