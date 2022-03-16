# System-wide .profile for sh(1)

# eval `$HOME/shctl/etc/rc`

_set_client_specific() {
	:
}

_set_bashisms() {
	if [ "${BASH-no}" != "no" ]; then
		[ -r "$HOME/.bashrc" ] && . "$HOME/.bashrc"
	fi
}

_set_cvs() {
	CVS_RSH=ssh
	export CVS_RSH
}

_set_gradle() {
	if [ -d /opt/gradle-2.12 ]; then
		GRADLE_HOME=/opt/gradle-2.12
		export GRADLE_HOME
	fi
}

_set_java() {
	if [ -x /usr/libexec/java_home ]; then
		if /usr/libexec/java_home 2>/dev/null; then
			JAVA_HOME=$(/usr/libexec/java_home)
			export JAVA_HOME
		fi
	fi
}

_set_less() {
	LESS="-FRSX"
	export LESS
	if [ -x /opt/pkg/bin/highlight ]; then
		LESSOPEN="| highlight %s --out-format xterm256 -l --force -s solarized-dark --no-trailing-nl"
		export LESSOPEN
	fi
}

_set_locale() {
	LC_CTYPE=en_US.UTF-8
	export LC_CTYPE
	LC_ALL=en_US.UTF-8
	export LC_ALL
}

_set_pyenv() {
	if type pyenv >/dev/null 2>&1; then
		PYENV_ROOT="$HOME/.pyenv"
		export PYENV_ROOT
		PATH="$PYENV_ROOT/bin:$PATH"
		eval "$(pyenv init -)"
		eval "$(pyenv virtualenv-init -)"
	fi
}

_set_sdkman() {
	if [ -d "$HOME/.sdkman" ]; then
		SDKMAN_DIR="/Users/schmonz/.sdkman"
		export SDKMAN_DIR
		if [ -s "$HOME/.sdkman/bin/sdkman-init.sh" ]; then
			. "$HOME/.sdkman/bin/sdkman-init.sh"
		fi
	fi
}

_set_termcolors() {
	CLICOLOR=1
	export CLICOLOR
	LSCOLORS=gxfxbEaEBxxEhEhBaDaCaD
	export LSCOLORS
	COLORTERM=1
	export COLORTERM
}

_set_cdpath() {
	CDPATH=".:$HOME:$HOME/trees:$HOME/Documents/trees:$HOME/trees/pkgsrc-cvs:$HOME/trees/pkgsrc:$HOME/Documents/trees/pkgsrc-cvs:$HOME/Documents/trees/pkgsrc"
	export CDPATH
}

_set_git() {
	GIT_PAGER='less -x9,17,25'
	export GIT_PAGER
}

_set_man() {
	if [ -x /opt/pkg/bin/bat ]; then
		MANPAGER="sh -c 'col -bx | bat -l man -p'"
		export MANPAGER
	fi
}

# <URL:https://unix.stackexchange.com/a/76256>
_set_predictable_ssh_auth_sock_location() {
	SOCK="/tmp/ssh-agent-${USER}-tmux"
	if [ ${SSH_AUTH_SOCK} ] && [ ${SSH_AUTH_SOCK} != ${SOCK} ]; then
		rm -f ${SOCK}
		ln -sf ${SSH_AUTH_SOCK} ${SOCK}
		SSH_AUTH_SOCK=${SOCK}
		export SSH_AUTH_SOCK
	fi
}

_exec_tmux_singleton_session() {
	if [ -x /opt/pkg/bin/tmux ] \
		&& [ -n "$PS1" ] \
		&& [ -z "$TMUX" ]; then
		{
			/opt/pkg/bin/tmux attach || exec /opt/pkg/bin/tmux new-session && exit
		}
	fi
}

_set_tmux() {
	if [ "buildbox" = "$USER" -a -z "$INTELLIJ_ENVIRONMENT_READER" ]; then
		_set_predictable_ssh_auth_sock_location
		_exec_tmux_singleton_session
	fi
}

_set_ssh() {
	if [ -z "$SSH_AUTH_SOCK" ]; then
		ssh-add -l >/dev/null || ssh-add --apple-load-keychain
		if [ -x /opt/pkg/bin/keychain ]; then
			eval $(/opt/pkg/bin/keychain --quiet --eval --agents ssh --inherit any id_rsa)
		fi
	fi
}

_set_client_specific
_set_bashisms
_set_cvs
_set_gradle
_set_java
_set_less
_set_locale
_set_pyenv
_set_sdkman
_set_termcolors
_set_cdpath
_set_git
_set_man
_set_tmux
_set_ssh
