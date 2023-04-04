_PKGSRC_PREFIX=/opt/pkg

# Search history for commands like what I've started typing
if [ "${BASH_VERSION}" ]; then
	bind '"\e[A":history-search-backward'
	bind '"\e[B":history-search-forward'
elif [ "${ZSH_VERSION}" ]; then
	bindkey "^[[A" history-search-backward
	bindkey "^[[B" history-search-forward
	autoload -Uz select-word-style && select-word-style bash
	ZLE_REMOVE_SUFFIX_CHARS=""
fi

if [ -f ${_PKGSRC_PREFIX}/share/asdf/asdf.sh ]; then
	. ${_PKGSRC_PREFIX}/share/asdf/asdf.sh
fi

alias emacs='emacs -nw'
pkgsrc_make_show_var() {
	make show-var VARNAME="$@"
}
alias msv='pkgsrc_make_show_var'
[ -x ${_PKGSRC_PREFIX}/bin/bat ] && alias cat='bat'

[ -r ~/pkg/share/examples/git ] && _GIT_PREFIX=~/pkg/share/examples/git
[ -r ${_PKGSRC_PREFIX}/share/examples/git ] && _GIT_PREFIX=${_PKGSRC_PREFIX}/share/examples/git
[ -r /usr/pkg/share/examples/git ] && _GIT_PREFIX=/usr/pkg/share/examples/git
#_GIT_PREFIX=/Applications/Xcode.app/Contents/Developer/usr/share/git-core

HISTSIZE=999
HISTFILE=${HOME}/.history
if [ "${BASH_VERSION}" ]; then
	for i in ${_PKGSRC_PREFIX}/share/bash-completion/completions/*; do
		. ${i}
	done
elif [ "${ZSH_VERSION}" ]; then
	setopt nosharehistory
	SAVEHIST=${HISTSIZE}
	autoload -Uz compinit && compinit
	autoload -Uz bashcompinit && bashcompinit
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

[ -r ~/.xsh ] && . ~/.xsh

if [ -x ${_PKGSRC_PREFIX}/bin/direnv ]; then
	if [ "${BASH_VERSION}" ]; then
		eval "$(direnv hook bash)"
	elif [ "${ZSH_VERSION}" ]; then
		eval "$(direnv hook zsh)"
	fi
fi

if [ -x ${_PKGSRC_PREFIX}/bin/sheldon ]; then
	if [ "${BASH_VERSION}" ]; then
		eval "$(SHELDON_PROFILE=bash sheldon source)"
	elif [ "${ZSH_VERSION}" ]; then
		eval "$(SHELDON_PROFILE=zsh sheldon source)"
	fi
fi
