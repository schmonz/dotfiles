default: none

none:

dotfiles: dotfiles-typical dotfiles-ssh dotfiles-synonyms dotfiles-agents

dotfiles-typical:
	for i in ackrc bashrc colordiffrc cvsignore cvsrc gitconfig gitignore_global inputrc profile tmux.conf vimrc; do \
		ln -s `pwd`/$${i} $${HOME}/.$${i} || true; \
	done

dotfiles-ssh:
	ln -s `pwd`/ssh-config $${HOME}/.ssh/config || true
	ln -s `pwd`/ssh-authorized-keys $${HOME}/.ssh/authorized_keys || true

dotfiles-agents:
	mkdir -p $${HOME}/.pi/agent
	ln -s `pwd`/pi-settings.json $${HOME}/.pi/agent/settings.json || true
	ln -s `pwd`/pi-i-have-adhd.json $${HOME}/.pi/agent/i-have-adhd.json || true
	mkdir -p $${HOME}/.claude
	ln -s `pwd`/claude-settings.json $${HOME}/.claude/settings.json || true

dotfiles-synonyms:
	ln -s .profile $${HOME}/.zprofile || true
	ln -s .bashrc $${HOME}/.zshrc || true
	ln -s .bashrc $${HOME}/.kshrc || true
