default: none

none:

dotfiles: dotfiles-typical dotfiles-ssh dotfiles-synonyms

dotfiles-typical:
	for i in ackrc bashrc colordiffrc cvsignore cvsrc gitconfig gitignore_global inputrc profile tmux.conf vimrc; do \
		ln -s `pwd`/$${i} $${HOME}/.$${i} || true; \
	done

dotfiles-ssh:
	ln -s `pwd`/ssh-config $${HOME}/.ssh/config || true
	ln -s `pwd`/ssh-authorized-keys $${HOME}/.ssh/authorized_keys || true

dotfiles-synonyms:
	ln -s .profile $${HOME}/.zprofile || true
	ln -s .bashrc $${HOME}/.zshrc || true
	ln -s .bashrc $${HOME}/.kshrc || true
