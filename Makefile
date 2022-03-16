default: none

none:

dotfiles:
	for i in ackrc bashrc colordiffrc cvsignore cvsrc gitconfig gitignore_global inputrc profile tmux.conf vimrc; do \
		ln -s `pwd`/$${i} $${HOME}/.$${i} || true; \
	done
