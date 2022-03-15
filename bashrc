# Search history for commands like what I've started typing
bind '"\e[A":history-search-backward'
bind '"\e[B":history-search-forward'

[ -r ~/pkg/share/examples/git ] && _GIT_PREFIX=~/pkg/share/examples/git
[ -r /opt/pkg/share/examples/git ] && _GIT_PREFIX=/opt/pkg/share/examples/git
[ -r /usr/pkg/share/examples/git ] && _GIT_PREFIX=/usr/pkg/share/examples/git
#_GIT_PREFIX=/Applications/Xcode.app/Contents/Developer/usr/share/git-core

if [ -f /opt/pkg/share/bash-completion/completions/git ]; then
	. /opt/pkg/share/bash-completion/completions/git
fi

if [ -f ${_GIT_PREFIX}/git-prompt.sh ]; then
	. ${_GIT_PREFIX}/git-prompt.sh
	#PROMPT_COMMAND='__git_ps1 "\u@\h:\w" "\\\$ "'
	PS1=": \u@\h:\w\e[0;32m\$(__git_ps1 '(%s)')\e[m;
:; "
	#GIT_PS1_SHOWDIRTYSTATE=1
	#GIT_PS1_SHOWSTASHSTATE=1
	#GIT_PS1_SHOWUNTRACKEDFILES=1
	GIT_PS1_SHOWUPSTREAM="auto"
	GIT_PS1_SHOWCOLORHINTS=1
else
	#PS1='\h:\W \u\$ '
	PS1=': \u@\h:\w;
:; '
fi

# BEGIN_KITTY_SHELL_INTEGRATION
if test -n "$KITTY_INSTALLATION_DIR" -a -e "$KITTY_INSTALLATION_DIR/shell-integration/bash/kitty.bash"; then source "$KITTY_INSTALLATION_DIR/shell-integration/bash/kitty.bash"; fi
# END_KITTY_SHELL_INTEGRATION

[ -r ~/.xsh ] && . ~/.xsh
