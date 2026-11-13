default: none

none:

# Run make from this checkout; path discovery stays in the shell, not make.
LINK = sh ./scripts/link-dotfile

.PHONY: default none dotfiles dotfiles-typical dotfiles-ssh dotfiles-synonyms \
	dotfiles-agents dotfiles-agents-generic dotfiles-agents-claude \
	dotfiles-agents-codex dotfiles-agents-pi test

dotfiles: dotfiles-typical dotfiles-ssh dotfiles-synonyms dotfiles-agents

dotfiles-typical:
	set -e; for i in ackrc bashrc colordiffrc cvsignore cvsrc gitconfig gitignore_global inputrc profile tmux.conf vimrc wezterm.lua; do \
		$(LINK) "$$(pwd)/$${i}" "$${HOME}/.$${i}"; \
	done

dotfiles-ssh:
	mkdir -p "$${HOME}/.ssh"
	$(LINK) "$$(pwd)/ssh-config" "$${HOME}/.ssh/config"
	$(LINK) "$$(pwd)/ssh-authorized-keys" "$${HOME}/.ssh/authorized_keys"

dotfiles-synonyms: dotfiles-typical
	$(LINK) "$${HOME}/.profile" "$${HOME}/.zprofile"
	$(LINK) "$${HOME}/.bashrc" "$${HOME}/.zshrc"
	$(LINK) "$${HOME}/.bashrc" "$${HOME}/.kshrc"

dotfiles-agents: dotfiles-agents-claude dotfiles-agents-codex dotfiles-agents-pi

# External skill checkouts may arrive after installation. See agents/README.md.
dotfiles-agents-generic:
	mkdir -p "$${HOME}/.agents/skills"
	$(LINK) --allow-missing "$${HOME}/.pi/agent/git/github.com/addyosmani/agent-skills/skills/doubt-driven-development" "$${HOME}/.agents/skills/doubt-driven-development"
	$(LINK) --allow-missing "$$(pwd)/../mavergreen-shipyard/claude-plugins/mavergreen/skills/mavergreen-conventions" "$${HOME}/.agents/skills/mavergreen-conventions"

dotfiles-agents-claude: dotfiles-agents-generic
	mkdir -p "$${HOME}/.claude"
	$(LINK) "$$(pwd)/agents/claude/settings.json" "$${HOME}/.claude/settings.json"

dotfiles-agents-codex: dotfiles-agents-generic
	mkdir -p "$${HOME}/.codex"
	$(LINK) "$$(pwd)/agents/codex/config.toml" "$${HOME}/.codex/config.toml"
	$(LINK) "$$(pwd)/agents/codex/AGENTS.md" "$${HOME}/.codex/AGENTS.md"

dotfiles-agents-pi: dotfiles-agents-generic
	mkdir -p "$${HOME}/.pi/agent"
	$(LINK) "$$(pwd)/agents/pi/settings.json" "$${HOME}/.pi/agent/settings.json"
	$(LINK) "$$(pwd)/agents/pi/i-have-adhd.json" "$${HOME}/.pi/agent/i-have-adhd.json"

test:
	PYTHONDONTWRITEBYTECODE=1 TEST_MAKE="$(MAKE)" python3 -m unittest discover -s tests
