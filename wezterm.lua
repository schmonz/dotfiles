-- Matches iTerm2's Default profile: JetBrainsMono Nerd Font 20, Solarized Dark.
local wezterm = require 'wezterm'
local config = wezterm.config_builder()

-- Noto Sans Symbols 2 has characters newer than 10.9's fonts, like U+23F5.
config.font = wezterm.font_with_fallback {
  'JetBrainsMono Nerd Font',
  'JetBrains Mono',
  'Noto Sans Symbols 2',
}
config.font_size = 20
-- iTerm2 draws no ligatures unless asked to.
config.harfbuzz_features = { 'calt=0', 'clig=0', 'liga=0' }

-- iTerm2's Solarized Dark preset stores its colours in a calibrated colour space and shows them
-- as Solarized's own sRGB values; WezTerm takes sRGB, so these are those.
config.colors = {
  foreground = '#839496',
  background = '#002b36',
  cursor_bg = '#839496',
  cursor_fg = '#073642',
  cursor_border = '#839496',
  selection_fg = '#93a1a1',
  selection_bg = '#073642',
  ansi = {
    '#073642', '#dc322f', '#859900', '#b58900',
    '#268bd2', '#d33682', '#2aa198', '#eee8d5',
  },
  brights = {
    '#002b36', '#cb4b16', '#586e75', '#657b83',
    '#839496', '#6c71c4', '#93a1a1', '#fdf6e3',
  },
}
config.bold_brightens_ansi_colors = 'BrightAndBold'

-- Full screen in its own Space, as other Mac apps do. Mavericks WezTerm opts its windows in
-- (NSWindowCollectionBehaviorFullScreenPrimary) since 20261026.072628-mavericks.2; before 10.11
-- toggleFullScreen: ignores a window without it.
config.native_macos_fullscreen_mode = true

return config
