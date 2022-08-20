-- Only required if you have packer configured as `opt`
-- vim.cmd [[packadd packer.nvim]]


-- 自动安装 Packer.nvim
-- 插件安装目录
-- ~/.local/share/nvim/site/pack/packer/
local fn = vim.fn
local install_path = fn.stdpath("data") .. "/site/pack/packer/start/packer.nvim"
local paccker_bootstrap
if fn.empty(fn.glob(install_path)) > 0 then
	vim.notify("正在安装Pakcer.nvim，请稍后...")
	paccker_bootstrap =
	fn.system(
		{
			"git",
			"clone",
			"--depth",
			"1",
			"https://github.com/wbthomason/packer.nvim",
			install_path
		}
	)

	-- https://github.com/wbthomason/packer.nvim/issues/750
	local rtp_addition = vim.fn.stdpath("data") .. "/site/pack/*/start/*"
	if not string.find(vim.o.runtimepath, rtp_addition) then
		vim.o.runtimepath = rtp_addition .. "," .. vim.o.runtimepath
	end
	vim.notify("Pakcer.nvim 安装完毕")
end

-- Use a protected call so we don't error out on first use
local status_ok, packer = pcall(require, "packer")
if not status_ok then
	vim.notify("没有安装 packer.nvim")
	return
end




packer.startup({
	function(use)
		-- Packer 可以升级自己
		use("wbthomason/packer.nvim")
		-------------------------- plugins -------------------------------------------

		-- 主题插件
		use("folke/tokyonight.nvim")

		-- 侧边文件管理
		use {
			'kyazdani42/nvim-tree.lua',
			requires = {
				'kyazdani42/nvim-web-devicons', -- optional, for file icons
			},
			tag = 'nightly' -- optional, updated every week. (see issue #1193)
		}

		-- 标签页
		use({ "akinsho/bufferline.nvim", tag = "v2.*",requires = { "kyazdani42/nvim-web-devicons", "moll/vim-bbye" }})

		-- 底部信息栏
		use({ "nvim-lualine/lualine.nvim", requires = { "kyazdani42/nvim-web-devicons" } })
		-- 展示进度
		use("arkav/lualine-lsp-progress")
		-- 文件搜索 
		use { 'nvim-telescope/telescope.nvim', requires = { "nvim-lua/plenary.nvim" } }
		-- 搜索环境变量
		use("LinArcX/telescope-env.nvim")

		-- 面板展示 
		use("glepnir/dashboard-nvim")
		-- 管理项目
		use("ahmedkhalf/project.nvim")
		-- neovim 的 lsp 
		use("nvim-treesitter/nvim-treesitter")
		use("nvim-treesitter/nvim-treesitter-context")
		--------------------- LSP --------------------

		use({ "williamboman/nvim-lsp-installer" })
		-- Lspconfig
		use({ "neovim/nvim-lspconfig" })

		-- 补全引擎
		use("hrsh7th/nvim-cmp")
		-- snippet 引擎
		use("hrsh7th/vim-vsnip")
		-- 补全源
		use("hrsh7th/cmp-vsnip")
		use("hrsh7th/cmp-nvim-lsp") -- { name = nvim_lsp }
		use("hrsh7th/cmp-buffer") -- { name = 'buffer' },
		use("hrsh7th/cmp-path") -- { name = 'path' }
		use("hrsh7th/cmp-cmdline") -- { name = 'cmdline' }
		-- go vim plugins 
		-- use("fatih/vim-go")
		use("kien/ctrlp.vim")
		-- 

		-- 常见编程语言代码段
		use("rafamadriz/friendly-snippets")
		-- ui (新增)
		use("onsails/lspkind-nvim")
		-- indent-blankline
		use("lukas-reineke/indent-blankline.nvim")
		use("tami5/lspsaga.nvim" )
		use {
			'lewis6991/gitsigns.nvim',
			-- tag = 'release' -- To use the latest release
		}
		use({ "jose-elias-alvarez/null-ls.nvim", requires = "nvim-lua/plenary.nvim" })
		use("liuchengxu/vista.vim")
		use("windwp/nvim-autopairs")
	end,
	config = {
		-- 并发数
		max_jobs = 16,
		-- 浮动窗口打开安装列表
		display = {
			open_fn = function ()
				return require("packer.util").float({ border = "single" })
			end
		},
	},
})

-- 每次保存 plugins.lua 自动安装插件
-- move to autocmds.lua
pcall(
	vim.cmd,
	[[
 augroup packer_user_config
 autocmd!
 autocmd BufWritePost plugins.lua source <afile> | PackerSync
 augroup end
 ]]
)

