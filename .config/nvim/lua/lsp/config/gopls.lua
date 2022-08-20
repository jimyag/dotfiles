vim.g.go_bin_path = "/Users/jimyag/gopath/bin"
local lspconfig = require("lspconfig")
local util = require("lspconfig/util")

local opts = {
	on_attach = function(client, bufnr)
		local function buf_set_keymap(...)
			vim.api.nvim_buf_set_keymap(bufnr, ...)
		end

		require("keybindings").mapLSP(buf_set_keymap)
		vim.cmd("autocmd BufWritePre <buffer> lua vim.lsp.buf.formatting_sync()")
	end,

	cmd = { "gopls", "serve" },
	filetypes = { "go", "gomod" },
	root_dir = util.root_pattern("go.work", "go.mod", ".git"),
	settings = {
		gopls = {
			analyses = {
				nilness = true,
				unusedparams = true,
				unusedwrite = true,
				useany = true,
			},
			experimentalPostfixCompletions = true,
			gofumpt = true,
			staticcheck = true,
			usePlaceholders = true,
			buildFlags = { "-tags=embed kodo ec28p4" },
			--env = {
			--	GOFLAGS = "-tags=embed",
			--},
		},
	},
}

return {
	on_setup = function(server)
		server:setup(opts)
	end,
}
