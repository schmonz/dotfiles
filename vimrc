" find all my installed plugins
runtime bundle/vim-pathogen/autoload/pathogen.vim
execute pathogen#infect()

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
colorscheme solarized
set cursorline
highlight clear SignColumn
let g:Powerline_symbols = 'unicode'

" VimRoom (<Leader>V)
let g:vimroom_sidebar_height=0
" set formatoptions=t1

" language-specific settings
filetype off
set runtimepath+=/Applications/LilyPond.app/Contents/Resources/share/lilypond/current/vim/
filetype on

autocmd BufRead,BufNewFile *.t,*.pl,*.pm setlocal filetype=perl
autocmd BufRead,BufNewFile *.toc setlocal filetype=asciidoc
autocmd BufRead,BufNewFile *.rb setlocal filetype=ruby
autocmd BufRead,BufNewFile *.txtl setlocal filetype=textile
autocmd BufEnter *.txtl let g:ikiwiki_render_filetype = 'textile'
autocmd BufRead,BufNewFile *.mdwn setlocal filetype=ikiwiki
autocmd BufEnter *.mdwn let g:ikiwiki_render_filetype = 'vim-markdown'
autocmd BufEnter * set nofoldenable
" autocmd BufEnter * set foldmethod=expr
" let g:ikiwiki_render_filetype = 'textile'
" ,*.mdwn set filetype=ikiwiki

function! IkiwikiPreview()
  :w
  let s:ikiwiki = "/usr/pkg/bin/ikiwiki --setup ~/Documents/wiki/conf/ikiwiki.conf --render"
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

autocmd BufEnter *.tt,*.ep,*.html,*.css setlocal tabstop=4 shiftwidth=4 nowrap
autocmd FileType perl,ruby,sh setlocal number|let w:m2=matchadd('Search', '\%>80v.\+', -1)
autocmd FileType ruby,cucumber setlocal expandtab tabstop=2 shiftwidth=2 softtabstop=2
autocmd FileType textile,markdown,ikiwiki setlocal expandtab tabstop=4 shiftwidth=4 softtabstop=4
autocmd FileType markdown,ikiwiki setlocal textwidth=72
autocmd FileType textile setlocal textwidth=0
" autocmd FileType perl iabbrev <buffer> iff if ()<left>

" shortcuts for paste mode in normal and insert modes
" nnoremap  :set invpaste paste?<cr>
" set pastetoggle=

" delete/change/etc text between parentheses
" to use: type 'dp' or 'cp' (etc.) while in normal mode
onoremap p i(

" configure Supertab
let g:SuperTabDefaultCompletionType = "context"
let g:SuperTabMidWordCompletion = "0"
" XXX YouCompleteMe is supposed to be better, but needs python bindings

" make the tmux status line show the currently-edited file
if &term == "screen" || &term == "screen-256color"
	set t_ts=
	set t_fs=
endif
if &term == "screen" || &term == "screen-256color" || &term == "xterm" || &term == "xterm-color" || &term == "xterm-256color"
	set title
endif
autocmd BufEnter * let &titlestring = "vim " . expand("%:h") . "/" . expand("%:t")

" mappings
noremap <leader>w !}fmt<cr>}b
noremap <leader>p :call IkiwikiPreview()<cr>
noremap <leader>f :call SelectaCommand("find * -type f", ":e")<cr>
noremap <leader>t :w\|:!make && clear && /usr/pkg/bin/prove -b %<cr>
" noremap <leader>t :w\|:!clear && /usr/pkg/bin/ruby193 %<cr>
" noremap <leader>t :w\|:!guess_how_to_run_tests_for_file %<cr>
" noremap <leader>t :w\|:!bmake clean && bmake test<cr>
" noremap <leader>t :w\|!clear && /Applications/LilyPond.app/Contents/Resources/bin/lilypond % && open berber.pdf<cr>
