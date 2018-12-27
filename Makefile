default: none

none:

dotfiles:
	for i in ackrc colordiffrc cvsignore cvsrc gitconfig gitignore_global tmux.conf vimrc; do \
		ln -s `pwd`/$${i} $${HOME}/.$${i} || true; \
	done
