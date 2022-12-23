set runtimepath+=/opt/pkg/share/lilypond/*/vim/
" find all my installed plugins
runtime bundle/vim-pathogen/autoload/pathogen.vim
execute pathogen#infect()

" 20170421 AATC schmonz:
" Filipe Silva (ninrod) suggested trying space as leader key -- either hand
" define <leader>
let mapleader = ","

" reload vim settings whenever I update them
autocmd! BufWritePost $MYVIMRC source $MYVIMRC

" make it easy to update them
nnoremap <leader>ev :split $MYVIMRC<cr>

" don't use arrow keys, they're too far away
nnoremap <up> <nop>
nnoremap <down> <nop>
nnoremap <left> <nop>
nnoremap <right> <nop>

" 20170420 AATC schmonz:
" Sam Livingston-Gray (geeksam) has this awesome hack for my shitty touchbar
imap jj <Esc>
" vmap jj <Esc>

" 20170713 schmonz:
nmap <silent> <C-k> <Plug>(ale_previous_wrap)
nmap <silent> <C-j> <Plug>(ale_next_wrap)

" fix common typos
iabbrev flase false
iabbrev udpate update

" DWIM searching
set incsearch
set ignorecase
set smartcase

" DWIM indenting
set autoindent
filetype plugin indent on
set cindent
inoremap # X<BS>#
set backspace=indent,eol,start
vnoremap <tab> >gv
vnoremap <s-tab> <gv

" DWIM commenting
autocmd FileType perl,ruby,sh,make	noremap <buffer> <leader># :s/^/#<cr>
autocmd FileType perl,ruby,sh,make	noremap <buffer> <leader>## :s/^#<cr>
autocmd FileType vim			noremap <buffer> <leader># :s/^/"<cr>
autocmd FileType vim			noremap <buffer> <leader>## :s/^"<cr>

" other general code settings
set showmatch
set ruler
set showmode
set visualbell
set scrolloff=3
set nojoinspaces
set nocompatible
set laststatus=2
set encoding=utf-8

" color
syntax on
set background=dark
set t_Co=16
let g:solarized_termcolors=16
" let g:lucius_contrast = 'medium'
colorscheme solarized
set cursorline
highlight clear SignColumn
let g:Powerline_symbols = 'unicode'

" VimRoom (<Leader>V)
let g:vimroom_sidebar_height=0
" let g:vimroom_width=120
" set formatoptions=t1

let g:hlvarcurrent = 1
autocmd BufRead,BufNewFile *.h1 setfiletype c
autocmd BufRead,BufNewFile *.t,*.pl,*.pm setfiletype perl
	autocmd FileType perl set updatetime=500
	autocmd FileType perl let g:hlvarcurrent = 0
autocmd BufRead,BufNewFile *.toc setfiletype asciidoc
autocmd BufRead,BufNewFile *.rb,Vagrantfile setfiletype ruby
autocmd BufRead,BufNewFile *.txtl setfiletype textile
autocmd BufRead,BufNewFile *.remark setfiletype markdown
	autocmd FileType textile let g:ikiwiki_render_filetype = 'textile'
" IWBNI FileType were 'ikiwiki', but how to set ikiwiki_render_filetype?
autocmd BufRead,BufNewFile *.mdwn setfiletype ikiwiki
autocmd BufRead,BufNewFile *.md setfiletype ikiwiki
	autocmd FileType ikiwiki let g:ikiwiki_render_filetype = 'vim-markdown'
autocmd BufRead,BufNewFile,BufEnter * set nofoldenable
autocmd BufEnter * call SmartTildes()
" autocmd BufEnter * set foldmethod=expr

function! SaveAndRunTests()
  :w
" let s:currentSub = PerlCurrentSub()
" let s:cmd = "! git commit --amend --no-edit"
" let s:cmd = "! git commit -am XXX"
" let s:cmd = "! clear && ginkgo"
" let s:cmd = "! clear && mix test"
" let s:cmd = "! clear && sbt test"
" let s:cmd = "! clear && cargo build && cargo run hi fred and chris"
" let s:cmd = "! clear && lein test"
" let s:cmd = "! clear && rspec %"
" let s:cmd = "! clear && c++ -I /opt/pkg/include -L /opt/pkg/lib -lstdc++ -lCppUTest -lCppUTestExt % && ./a.out"
" let s:cmd = "! clear && make"
" let s:cmd = "! clear && make -f Makefile.boot"
" let s:cmd = "! clear && cd .. && make -f Makefile.boot && cd testsuite && bmake check-simple VERBOSE=no && bmake clean VERBOSE=no"
" let s:cmd = "! clear && ./test-logstderr"
" let s:cmd = "! clear && ./run-once.sh"
" let s:cmd = "! clear && cc % && ./a.out"
" let s:cmd = "! clear && ruby *_test.rb"
" let s:cmd = "! clear && jasmine-node ."
" let s:cmd = "! clear && ./% secretbombdisarmingcodes.txt"
" let s:cmd = "! clear && ./%"
" let s:cmd = "! clear && make && clear && prove -b %"
" let s:cmd = "! clear && go test"
" let s:cmd = "! clear && env IKIWIKI_TEST_ASSUME_MODERN_DISCOUNT=1 %"
" let s:cmd = "! clear && elixir bob_test.exs"
" let s:cmd = "! clear && prove -b t/import.t"
" let s:cmd = "! clear && prove -PProgressBar -b t"
" let s:cmd = "! clear && prove -PProgressBar::Each -b t/import.t"
" let s:cmd = ":w\|:! open -a /Applications/Chromium.app %"
" let s:cmd = "! clear && make fixsmtpio && clear && tcpserver 0 2626 env FIXSMTPIODEBUG=1 /Users/schmonz/Documents/trees/qmail/fixsmtpio ofmipd"
" let s:cmd = "! clear && make acceptutils && sudo tcpserver 0 26 ./authup smtp checkpassword-pam -s sshd ./fixsmtpio ofmipd"
" let s:cmd = "! clear && make acceptutils && sudo tcpserver 0 2626 ./reup -t 5 ./authup smtp checkpassword-pam -s sshd ofmipd"
" let s:cmd = "! clear && make acceptutils && sudo sslserver -n 0 110 ./authup pop3 checkpassword-pam -s sshd qmail-pop3d Maildir"
" let s:cmd = "! clear && nroff -man % | less -p 'CONTROL FILES'"
" let s:cmd = "! clear && nroff -man % | less"
" let s:cmd = "! clear && make fixsmtpio && clear && env FIXSMTPIODEBUG=1 ./fixsmtpio ofmipd 2>log"
" let s:cmd = "! clear && make acceptutils-tests && clear && make acceptutils-tests-run"
" let s:cmd = VimuxRunCommand("make acceptutils-tests-run")
" let s:cmd = "! clear && PYTHONPATH=test:$PYTHONPATH py.test %"
" let s:cmd = "! clear && ./% < sample_message_in.txt"
" let s:cmd = "! clear && python2.7 ./io_strangler.py smtp env RELAYCLIENT= ofmipd 2>strangler.log"
" let s:cmd = "! clear && tcpserver 0 5888 ./io_strangler.py smtp env RELAYCLIENT= ofmipd"
" let s:cmd = "! clear && python2.7 ./io_strangler.py pop3 qmail-pop3d /var/tmp/schmonz-maildir 2>strangler.log"
" let s:cmd = "! clear && python2.7 ./io_strangler.py http /opt/pkg/libexec/bozohttpd -e /Users/schmonz/Sites localhost 2>strangler.log"
" let s:cmd = "! clear && mconnect 0 5888"
" let s:cmd = "! clear && ./% echo hi"
  execute s:cmd
" noremap <leader>t :w\|:!clear && /opt/pkg/bin/ruby193 %<cr>
" noremap <leader>t :w\|:!guess_how_to_run_tests_for_file %<cr>
" noremap <leader>t :w\|:!bmake clean && bmake test<cr>
" noremap <leader>t :w\|!clear && /Applications/LilyPond.app/Contents/Resources/bin/lilypond % && open berber.pdf<cr>
endfunction

function! IkiwikiPreview()
  :w
  let s:ikiwiki = "/opt/pkg/bin/ikiwiki --setup ~/Documents/wiki/conf/ikiwiki --render"
  let s:currentFile = expand("%")
  let s:tmpFile = s:currentFile . ".tmp.html"
  let s:cmd = "silent ! " . s:ikiwiki . " " . s:currentFile . " > " . s:tmpFile . " && open " . s:tmpFile . " && sleep 5 && rm " . s:tmpFile
  execute s:cmd
  redraw!
endfunction

function! SelectaCommand(choice_command, vim_command)
  try
    silent! exec a:vim_command . " " . system(a:choice_command . " | selecta")
  catch /Vim:Interrupt/
    " Swallow the ^C so that the redraw below happens; otherwise there will be
    " leftovers from selecta on the screen
  endtry
  redraw!
endfunction

" http://blogs.perl.org/users/ovid/2011/01/show-perl-subname-in-vim-statusline.html
" doesn't work with line numbers on
if has('perl')
perl << EOP
  use strict;
  sub current_sub {
    my $curwin = $main::curwin;
    my $curbuf = $main::curbuf;

    my @document = map { $curbuf->Get($_) } 0 .. $curbuf->Count;
    my ($line_number, $column) = $curwin->Cursor;

    my $sub_name = '(not in sub)';
    for my $i (reverse (1 .. $line_number-1)) {
      my $line = $document[$i];
      if ($line =~ /^\s*sub\s+(\w+)\b/) {
        $sub_name = $1;
        last;
      }
    }
    VIM::DoCommand "let subName='$line_number: $sub_name'";
  }
EOP

function! PerlCurrentSub()
  perl current_sub()
  return subName
endfunction
endif

autocmd BufEnter *.tt,*.ep,*.html,*.css setlocal tabstop=4 shiftwidth=4 nowrap
autocmd FileType perl,ruby,sh,javascript,c,cpp setlocal number|let w:m2=matchadd('Search', '\%>80v.\+', -1)
" autocmd FileType rust,perl setlocal number expandtab tabstop=4 shiftwidth=4 softtabstop=4
autocmd FileType rust setlocal number expandtab tabstop=4 shiftwidth=4 softtabstop=4
autocmd FileType python setlocal number expandtab tabstop=4 shiftwidth=4 softtabstop=0
autocmd FileType ruby,cucumber,hb,haskell,scala,go,lua,c setlocal number expandtab tabstop=2 shiftwidth=2 softtabstop=2
autocmd FileType textile,markdown,ikiwiki,javascript,objc,cpp setlocal expandtab tabstop=4 shiftwidth=4 softtabstop=4
" autocmd FileType c setlocal tabstop=8 shiftwidth=8 softtabstop=8
autocmd FileType markdown,ikiwiki setlocal textwidth=72
autocmd FileType textile,markdown,ikiwiki setlocal textwidth=0|let gitgutter_enabled=0
autocmd FileType perl nnoremap ,pt :%!perltidy -q<cr>
autocmd FileType perl vnoremap ,pt :!perltidy -q<cr>
" autocmd FileType perl iabbrev <buffer> iff if ()<left>

function! SmartTildes()
	if &number
		" color non-text lines same as background
		highlight NonText ctermfg=bg guifg=bg
	endif
	" gonna want to set to set it back when I switch out of numbered
	" http://www.ibm.com/developerworks/library/l-vim-script-1/
endfunction

" shortcuts for paste mode in normal and insert modes
" nnoremap  :set invpaste paste?<cr>
" set pastetoggle=

" delete/change/etc text between parentheses
" to use: type 'dp' or 'cp' (etc.) while in normal mode
onoremap p i(

" configure syntastic
" let g:syntastic_perl_checkers = ['perl', 'perlcritic']
let g:syntastic_perl_checkers = ['perl']
let g:syntastic_enable_perl_checker = 1
let g:syntastic_c_include_dirs = ['/Users/schmonz/pkg/include']
let g:syntastic_python_checkers = ['python']

" configure CtrlP
let g:ctrlp_map = '<c-p>'
let g:ctrlp_cmd = 'CtrlP'

" configure Supertab
let g:SuperTabDefaultCompletionType = "context"
let g:SuperTabMidWordCompletion = "0"
" XXX YouCompleteMe is supposed to be better, but needs python bindings

" configure ack.vim
if executable('ag')
	let g:ackprg = 'ag --vimgrep'
endif

" make the tmux status line show the currently-edited file
if &term == "screen" || &term == "screen-256color"
	set t_ts=
	set t_fs=
endif
if &term == "screen" || &term == "screen-256color" || &term == "xterm" || &term == "xterm-color" || &term == "xterm-256color"
	set title
endif
autocmd BufEnter * let &titlestring = "vim " . expand("%:h") . "/" . expand("%:t")

" configure ale
let g:ale_perl_perl_executable = 'prove'

" mappings
nnoremap <leader>w !} perl -MText::Autoformat -e "{autoformat{break=>break_wrap};}" \| sed '${/^$/d;}'<cr>
noremap <leader>p :call IkiwikiPreview()<cr>
noremap <leader>f :call SelectaCommand("find * -type f", ":e")<cr>
noremap <leader>t :call SaveAndRunTests()<cr>
" noremap <leader>t :w<cr>:Dispatch make acceptutils-tests-run<cr>

" https://twitter.com/jschauma/status/983810191346032641
function! ToggleTabs()
	if &list
		set nolist
	else
		set list
		silent! listchars=tab:>.,trail:>,precedes:<
	endif
endfunction
map <Leader>	 :call ToggleTabs()<CR>
