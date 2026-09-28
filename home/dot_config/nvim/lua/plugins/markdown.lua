---@type LazySpec
return {
  {
    "MeanderingProgrammer/render-markdown.nvim",
    ft = "markdown",
    dependencies = { "nvim-treesitter/nvim-treesitter", "nvim-mini/mini.icons" },
    opts = {},
  },
  {
    "kais-radwan/ascii-mermaid",
    ft = "markdown",
    opts = { display_mode = "replace" },
  },
}
