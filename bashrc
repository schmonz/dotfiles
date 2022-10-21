# Search history for commands like what I've started typing
if [ "${BASH_VERSION}" ]; then
	bind '"\e[A":history-search-backward'
	bind '"\e[B":history-search-forward'
elif [ "${ZSH_VERSION}" ]; then
	bindkey "^[[A" history-beginning-search-backward
	bindkey "^[[B" history-beginning-search-forward
fi

alias emacs='emacs -nw'
pkgsrc_make_show_var() {
	make show-var VARNAME="$@"
}
alias msv='pkgsrc_make_show_var'

[ -r ~/pkg/share/examples/git ] && _GIT_PREFIX=~/pkg/share/examples/git
[ -r /opt/pkg/share/examples/git ] && _GIT_PREFIX=/opt/pkg/share/examples/git
[ -r /usr/pkg/share/examples/git ] && _GIT_PREFIX=/usr/pkg/share/examples/git
#_GIT_PREFIX=/Applications/Xcode.app/Contents/Developer/usr/share/git-core

if [ "${BASH_VERSION}" ] && [ -f /opt/pkg/share/bash-completion/completions/git ]; then
	. /opt/pkg/share/bash-completion/completions/git
elif [ "${ZSH_VERSION}" ] && [ -f /opt/pkg/share/zsh/site-functions/_git ]; then
	autoload -Uz compinit && compinit
fi

if [ -f ${_GIT_PREFIX}/git-prompt.sh ]; then
	. ${_GIT_PREFIX}/git-prompt.sh
	#GIT_PS1_SHOWDIRTYSTATE=1
	#GIT_PS1_SHOWSTASHSTATE=1
	#GIT_PS1_SHOWUNTRACKEDFILES=1
	GIT_PS1_SHOWUPSTREAM="auto"
	GIT_PS1_SHOWCOLORHINTS=1

	#PROMPT_COMMAND='__git_ps1 "\u@\h:\w" "\\\$ "'

	if [ "${BASH_VERSION}" ]; then
		PS1=": \u@\h:\w\e[0;32m\$(__git_ps1 '(%s)')\e[m;
:; "
	elif [ "${ZSH_VERSION}" ]; then
		setopt prompt_subst
		PROMPT=': %n@%m:%~$(__git_ps1 "(%s)");
:; '
		autoload -U promptinit && promptinit
	else
		#PS1='\h:\W \u\$ '
		PS1=': \u@\h:\w;
:; '
	fi
fi

# BEGIN_KITTY_SHELL_INTEGRATION
if test -n "$KITTY_INSTALLATION_DIR" -a -e "$KITTY_INSTALLATION_DIR/shell-integration/bash/kitty.bash"; then source "$KITTY_INSTALLATION_DIR/shell-integration/bash/kitty.bash"; fi
# END_KITTY_SHELL_INTEGRATION

[ -r ~/.xsh ] && . ~/.xsh
