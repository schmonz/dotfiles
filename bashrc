# Shared by Bash, Zsh, and Ksh; keep interactive setup out of batch/SSH commands.
case $- in
	*i*) ;;
	*) return 0 ;;
esac

# Standalone/non-login shells also need discovery; an uninstalled helper is optional.
_dotfiles_command() { return 1; }
_dotfiles_support_file() { return 1; }
if [ -f "$HOME/.shell-common" ] && [ -r "$HOME/.shell-common" ]; then
	. "$HOME/.shell-common"
fi

_PKGSRC_PREFIX=/opt/pkg
if [ -d "$HOME/pkg" ]; then
	_PKGSRC_PREFIX=$HOME/pkg
fi

# Search history for commands like what I've started typing
if [ "${BASH_VERSION}" ]; then
	bind '"\e[A":history-search-backward'
	bind '"\e[B":history-search-forward'
elif [ "${ZSH_VERSION}" ]; then
	bindkey "^[[A" history-search-backward
	bindkey "^[[B" history-search-forward
	autoload -Uz select-word-style && select-word-style bash
	ZLE_REMOVE_SUFFIX_CHARS=""
else
	:
fi

alias emacs='emacs -nw'
pkgsrc_make_show_var() {
	make show-var VARNAME="$@"
}
alias msv='pkgsrc_make_show_var'
alias mic='make install clean'
alias ag="ag --pager='less ${LESS}'"
if _bat=$(_dotfiles_command bat); then alias cat="$(_dotfiles_quote "$_bat")"; fi
if _vim=$(_dotfiles_command vim); then alias vi="$(_dotfiles_quote "$_vim")"; fi

HISTSIZE=999
HISTFILE=${HOME}/.history
if [ "${BASH_VERSION}" ]; then
	# Current bash-completion requires Bash 4.2+. Keep basic completion on older Bash.
	if [ "${BASH_VERSINFO[0]}" -gt 4 ] ||
		{ [ "${BASH_VERSINFO[0]}" -eq 4 ] && [ "${BASH_VERSINFO[1]}" -ge 2 ]; }; then
		if _completion=$(_dotfiles_support_file "$BASH" \
			share/bash-completion/bash_completion etc/bash_completion); then
			if . "$_completion"; then :; fi
		fi
	fi
elif [ "${ZSH_VERSION}" ]; then
	setopt nosharehistory
	SAVEHIST=${HISTSIZE}
	autoload -Uz compinit && compinit
	autoload -Uz bashcompinit && bashcompinit
else
	:
fi

if _git_prompt=$(_dotfiles_support_file git \
	share/examples/git/git-prompt.sh share/git/completion/git-prompt.sh \
	lib/git-core/git-sh-prompt share/git-core/contrib/completion/git-prompt.sh \
	share/git-core/git-prompt.sh); then
	_GIT_PREFIX=${_git_prompt%/*}
	if [ "${BASH_VERSION}" ]; then
		if . "$_git_prompt"; then :; fi
	elif [ "${ZSH_VERSION}" ]; then
		if . "$_git_prompt"; then :; fi
	else
		:
	fi

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
		PS1=': $(whoami)@$(hostname -s):$(pwd);
:; '
	fi
fi

[ -r ~/.xsh ] && . ~/.xsh

if [ "${BASH_VERSION}" ]; then
	_dotfiles_shell=bash
elif [ "${ZSH_VERSION}" ]; then
	_dotfiles_shell=zsh
elif [ "${KSH_VERSION}" ]; then
	_dotfiles_shell=ksh
else
	_dotfiles_shell=posix
fi

if _direnv=$(_dotfiles_command direnv); then
	eval "$(_dotfiles_hook "$_direnv" hook "$_dotfiles_shell")"
fi

if _sheldon=$(_dotfiles_command sheldon); then
	case $_dotfiles_shell in
		bash|zsh) eval "$(SHELDON_PROFILE=$_dotfiles_shell _dotfiles_hook "$_sheldon" source)" ;;
	esac
fi

if _starship=$(_dotfiles_command starship); then
	eval "$(_dotfiles_hook "$_starship" init "$_dotfiles_shell")"
fi

if _zoxide=$(_dotfiles_command zoxide); then
	case $_dotfiles_shell in
		bash|zsh) eval "$(_dotfiles_hook "$_zoxide" init "$_dotfiles_shell")" ;;
		*) eval "$(_dotfiles_hook "$_zoxide" init posix --hook prompt)" ;;
	esac
fi

# iTerm2 sets TERM_PROGRAM locally; since 3.3 it also sets LC_TERMINAL, which SSH forwards.
# Its installer appends a hook unless this file mentions iterm2_shell_integration.
if [ "${LC_TERMINAL-}" = iTerm2 ] || [ "${TERM_PROGRAM-}" = iTerm.app ]; then
	case $_dotfiles_shell in
		bash|zsh)
			_iterm2_integration=$HOME/.iterm2_shell_integration.$_dotfiles_shell
			if [ -f "$_iterm2_integration" ] && [ -r "$_iterm2_integration" ]; then
				if . "$_iterm2_integration"; then :; fi
			else
				printf '%s\n' "dotfiles: no $_iterm2_integration; run iTerm2 > Install Shell Integration" >&2
			fi
			;;
	esac
fi

# Optional hook feature probes may return false after successfully defining hooks.
:
