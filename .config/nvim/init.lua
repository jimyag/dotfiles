require('basic')

-- 快捷键映射
require("keybindings")

-- Packer 插件管理
require("plugins")

-- 主题设置 （新增）
require("colorscheme")

require("plugin-config.nvim-tree")
require("plugin-config.bufferline")
require("plugin-config.lualine")
require("plugin-config.telescope")
require("plugin-config.dashboard")
require("plugin-config.project")
require("plugin-config.nvim-treesitter")
require("plugin-config.nvim-treesitter-context")
require("plugin-config.indent-blankline")
require("plugin-config.gitsigns")
require("plugin-config.vista")
require("plugin-config.nvim-autopairs")
-- lsp 
require("lsp.setup")
require("lsp.cmp")
require("lsp.ui")
require("lsp.null-ls")
